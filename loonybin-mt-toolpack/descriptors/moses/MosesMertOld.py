from loonybin import Tool
from Moses import Moses

class MosesMert(Tool):
    
    def __init__(self):
        self.decoder = Moses()
    
    def getName(self):
        return 'Machine Translation/Tuning/Moses MERT (Old)'
    
    def getDescription(self):
        return "Tunes a translation system, decoding with Moses and using Moses' old implementation of MERT (works with 'unlimited' TM features). This DOES NOT FILTER PHRASE TABLES by default. You are expected to do this externally."
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        params = self.decoder.getSharedParams()
        return params

    def getInputNames(self, params):
        inputs = self.decoder.getSharedInputs(params)
        inputs.extend([ ('fCorpus','?'),
                        ('refs','?'),
                        ('lambdas','file containing a lambdas string for tuning as described in the Moses --lambda documentation (e.g. d:1,0.5-1.5 lm:1,0.5-1.5 tm:0.3,0.25-0.75;0.2,0.25-0.75;0.2,0.25-0.75;0.3,0.25-0.75;0,-0.5-0.5 w:0,-0.5-0.5)')])
        return inputs

    def getOutputNames(self, params):
        return [ ('finalConfigFile','?'),
		 	    ('finalNbest','?') ]
    
    def getCommands(self, params, inputs, outputs):

        # Create base moses.ini on the fly
        commands = self.decoder.makeConfigFileCommands(params, inputs, 'moses.ini')

        # Separate references into separate files as Moses expects
        commands.append('mkdir separate-reference-files')
        commands.append('numRefs=$(( $( wc -l < %(refs)s ) / $( wc -l < %(fCorpus)s ) ))'%inputs)
        commands.append(r'awk "BEGIN{i=0} {print>>(\"separate-reference-files/ref\"i);i+=1;i%=$numRefs}" <'+inputs['refs'])
    
        # leave off all mentions of features?
        commands.append('./scripts/training/absolutize_moses_model.pl moses.ini > moses.abs.ini')
        commands.append('./scripts/training/mert-moses.pl `pwd`/%(fCorpus)s `pwd`/separate-reference-files/ref `pwd`/moses-cmd/src/moses `pwd`/moses.abs.ini --rootdir `pwd`/scripts --working-dir `pwd`/mert-work --lambdas="`cat %(lambdas)s`" --no-filter-phrase-table  2>&1 | tee mert.log'%inputs)
        commands.append('ln -s ../mert-work/moses.ini %(finalConfigFile)s'%outputs)
        commands.append('finalNbestGz=$(ls -t mert-work/run*.best*.out.gz | head -1)')
        commands.append('zcat $finalNbestGz > %(finalNbest)s'%outputs)
        
        return commands
    
    def getPreAnalyzers(self, params, inputs):
        # TODO: Log entire config file
        # TODO: Make sure we don't have any blank inputs
        #cmd = ('AnalyzeParCorpus.sh %(fCorpusOut)s %(eCorpusOut)s'%outputs
        #       )
        return [ ]

    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: Make sure we have the same number of output hypotheses as inputs
        #cmd = ('extract_zmert_stats.pl zmert.stdout %(paramConfigFile)s'%inputs)
        return [ ]

    def getStatus(self, params, inputs):
        return [ "egrep -o 'iteration [0-9]+' \"$(ls -t mert-work/run*.moses.ini | head -1)\"",
                 "egrep -ho 'BLEU .* on dev' \"$(ls -t mert-work/run*.moses.ini | head -1)\" | sed 's/on dev//g'" ]

if __name__ == '__main__':
    import sys
    t = MosesMert()
    t.handle(sys.argv)
    
