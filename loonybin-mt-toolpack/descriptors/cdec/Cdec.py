from loonybin import Tool

class Cdec(Tool):
    
    def getName(self):
        return 'Machine Translation/Decoders/Cdec'
    
    def getDescription(self):
        return """
Takes a translation grammar and language model and produces n-best translation hypotheses using cdec.
"""
    
    def getRequiredPaths(self):
        return ['cdec']

    # Decoder params shared with MERT
    def getSharedParams(self):
         return [ ('lmOrder', 'Order of the language model'),
                  ('useGLC', 'Use Global lexical coherence features?'),
                  ('glcUseNull', 'Use NULL word?') ]

    def getParamNames(self):
        params = self.getSharedParams()
        params.append( ('kBest','number of k-best hypotheses to extract') )
        return params
   
    # Decoder params shared with MERT
    def getSharedInputs(self, params):
        inputs = [ ('lmFile', 'ARPA format language model'),
                 ('tmFile', 'Cdec-format translation model'),
                 #('glueFile', 'Cdec-format glue grammar')
                   ]
        if self.isTrue(params['useGLC']):
            inputs.append( ('glcSrcVocab','Source vocab recognized by GLC feature') )
            inputs.append( ('glcTgtVocab','Target vocab recognized by GLC feature') )
            inputs.append( ('glcSrcStopwords','Source stopword list for GLC') )
            inputs.append( ('glcTgtStopwords','Target stopword list for GLC') )
            inputs.append( ('glcCooc', 'Coocurrence matrix for GLC') )
            inputs.append( ('glcFeatWeights','Feature weights for GLC') )
        return inputs

    def getInputNames(self, params):
        inputs = self.getSharedInputs(params)
        inputs.extend([ ('fSents', '"French" sentences for which n-best hypotheses will be produced'),
                        ('optimizedWeightsFile', 'Final configuration file resulting from MERT containing optimized feature weights') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('eKBest', '"English" n-best hypotheses in cdec format') ]
    
    def makeConfigFileCommands(self, params, inputs, configFileName):
           
		config = []
		config.append('formalism=scfg')
		config.append('grammar=$(pwd)/%(tmFile)s'%inputs)
		#config.append('scfg_extra_glue_grammar=`pwd`/%(glueFile)s'%inputs)
		config.append('feature_function=LanguageModel -o %s $(pwd)/%s'%(params['lmOrder'], inputs['lmFile']) )
		config.append('feature_function=WordPenalty')
		config.append('add_pass_through_rules=true')
		config.append('unique_k_best=true')
		#config.append('cubepruning_pop_limit=200')
		
                if self.isTrue(params['useGLC']):
                    config.append('feature_function=ContextCRF -s $PWD/%(glcSrcVocab)s -t $PWD/%(glcTgtVocab)s -sstop $PWD/%(glcSrcStopwords)s -tstop %(glcTgtStopwords)s -f $PWD/%(glcFeatWeights)s -c $PWD/%(glcCooc)s'%inputs)
                    config.append('feature_function=WordSet -N crf.ContentWordCount -v $PWD/%(glcTgtVocab)s'%inputs)
                    config.append('feature_function=WordSet -N crf.NonContentWordCount -v $PWD/%(glcTgtVocab)s --oov'%inputs)
                    config.append('feature_function=WordSet -N crf.StopWordCount -v $PWD/%(glcTgtStopwords)s'%inputs)
                    config.append('feature_function=WordSet -N crf.NonStopWordCount -v $PWD/%(glcTgtStopwords)s --oov'%inputs)

                if self.isTrue(params['glcUseNull']):
                    raise Exception('TODO: Implement me')

		commands = []
		for line in config:
		    commands.append('echo "' + line + '" >> ' + configFileName)
            
		return commands
    
    def getCommands(self, params, inputs, outputs):
     
        commands = self.makeConfigFileCommands(params, inputs, 'cdec.ini')
        commands.append('./decoder/cdec -c cdec.ini -i %(fSents)s -w %(optimizedWeightsFile)s -r -P'%inputs +
                        ' -k %(kBest)s'%params +
                        ' > %(eKBest)s'%outputs)
        return commands

    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: More detailed analysis of output
        #cmd = ('extract_feature_data.py %(eNBestOut)s'%outputs +
        #       ' %(optimizedConfigFile)s'%inputs)
        return [ ]

if __name__ == '__main__':
    import sys
    t = Cdec()
    t.handle(sys.argv)
