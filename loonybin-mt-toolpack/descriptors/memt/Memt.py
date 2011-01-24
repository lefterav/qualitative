from loonybin import Tool

class Memt(Tool):
    
    def getName(self):
        return 'Machine Translation/MEMT/MEMT Decode'
    
    def getDescription(self):
        return "Decode sentences to produce topbest and n-best hypotheses using tuned weights"
    
    def getInputNames(self, params):
        inputs = self.getSharedInputs()
        inputs.extend([
                       ('tunedWeights','?'),
                       ('testMatchedFile','?')
                       ])
        return inputs
    
    def getOutputNames(self, params):
        return [ ('topbestHypotheses','?'),
                 ('nbestHypotheses','?') ]
        
    def getParamNames(self):
        return self.getSharedParams()
    
    def getRequiredPaths(self):
        return ['memt']

    def getSharedInputs(self):
        return [ ('lmFile','ARPA-format language model') ]

    def getSharedParams(self):
        return [ ('align.transitive','Make alignments transitive?'),
                ('beam_size','Size of the decoder\'s internal search beam'),
                ('length_normalize','Langth normalize before comparing sentence end scores?'),
                ('phrase.type','Phrase types (space-delimited list: punctuation, alignment) to use -- legacy option'),
                ('legacy.continue_recent','Allow continuation from the most recently used'),
                ('legacy.extend_aligned','Extend using aligned words?'),
                ('horizon.stay_weights','System weights for purposes of voting on staying or skipping.  Default is uniform.'),
                ('horizon.stay_threshold','Sum of stay_weights required to stay -- only applies if horizon.method=alignment'),
                ('horizon.radius','How long a word can linger'),
                ('horizon.method','Horizon method: length or alignment'),
                ('score.verbatim0.individual','Maximum n-gram length to report per-system verbatim scores features'),
                ('score.verbatim0.collective','Maximum n-gram length to report collective (averaged over systems) verbatim features. collective >= individual.'),
                ('score.verbatim0.mask','Space separated list of alignment types to include.'),
                ('score.verbatim1.individual','Maximum n-gram length to report per-system verbatim scores features'),
                ('score.verbatim1.collective','Maximum n-gram length to report collective (averaged over systems) verbatim features. collective >= individual.'),
                ('score.verbatim1.mask','Space separated list of alignment types to include.'),
                ('output.nbest','Number of n-best hypotheses'),
                ('output.caps','Set true to preserve case'),
                ('output.scores','Include scores in output?'),
                ('output.alignment','Include alignment back to a source hypothesis?')
                ]
    
    def makeConfigFile(self, params, configFilename, weightsCommand=''):
        lines = []
        for (key, value) in params.iteritems():
            lines.append( '%s = "%s"'%(key,value) )
            
        commands = []
        for line in lines:
            commands.append( "echo '%s' >> %s"%(line, configFilename) )
                            
        if weightsCommand:
            commands.append( 'echo score.weights = '"'    %s'"''%weightsCommand )
        
        return commands
        
    def getStartServerCommands(self, params, inputs, outputs):
        commands= []
        startServer = './scripts/server.sh --lm.file %(lmFile)s '%inputs + ' > portFile &'%params
        commands.append(startServer)
        getPid = 'pid=$!'
        commands.append(getPid)
        getPort = "port=`cut -d' ' -f5 portFile`"
        commands.append(getPort)
        return commands
    
    def getKillServerCommands(self):
        return ['kill $pid']
    
    def getCommands(self, params, inputs, outputs):
        commands = Memt.getStartServerCommands(self, params, inputs, outputs)
        commands.extend(self.makeConfigFile(params, 'decoder.config', 'cat %(tunedWeights)s'%inputs))
        
        runClient = './simple_decode.sh $port decoder.config %(testMatchedFile)s'%inputs
        commands.append(runClient)
        
        commands.extend(Memt.getKillServerCommands(self))
        
        commands.append('ln -s output.1best %(topbestHypotheses)s'%outputs)
        commands.append('ln -s output.nbest %(nbestHypotheses)s'%outputs)
        return commands
    
if __name__ == '__main__':
    import sys
    t = Memt()
    t.handle(sys.argv)