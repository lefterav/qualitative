from loonybin import Tool
from Moses import Moses

class MosesMert(Tool):
    
    def __init__(self):
        self.decoder = Moses()
    
    def getName(self):
        return 'Machine Translation/Tuning/Moses MERT (New)'
    
    def getDescription(self):
        return "Tunes a translation system, decoding with Moses and using Moses' new implementation of MERT (works with 5 TM features)"
    
    def getRequiredPaths(self):
        return ['moses']

    def getParamNames(self):
        params = self.decoder.getSharedParams()
        return params

    def getInputNames(self, params):
        inputs = self.decoder.getSharedInputs(params)
        inputs.extend([ ('fCorpus','tokenized foreign sentences on which we will tune, one sentence per line'),
                        ('refs','tokenized interlaced references, one reference sentence per line with references for one source sentence followed immediately by all references for the next source sentence') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('finalConfigFile','Moses configuration file containing the optimized parameters'),
				 ('finalNbest','Moses-format n-best list from the final iteration of MERT (NOT necessarily equivalent to the topbest list that would be produced by redecoding with the final parameters)') ]
    
    def getCommands(self, params, inputs, outputs):
    	
    	# Create base moses.ini on the fly
		commands = self.decoder.makeConfigFileCommands(params, inputs, 'moses.ini')

		# Hack around bug in phrase table filtering that creates a corrupt config file
		# for when using multiple LMs
		noFilter = ''
		numLms = self.decoder.getNumLms(params)
		if numLms > 1:
			noFiler = ' --no-filter '
			commands.append('echo >&2 "WARNING: Not filtering phrase table due to use of multiple language models (hack around PT filtering bug)"')
		
		commands.append('dir=$(pwd)')
		commands.append('mkdir mert-work')
		
		# Unpack references from single file into multiple files
		# with the prefix $dir/separate-reference-files/ref
		# and ending with ...ref0, ...ref1, etc
	        # TODO: Share this code with cdec instead of using abject-oriented inheritance
		commands.append('mkdir separate-reference-files')
                commands.append('numRefs=$(( $( wc -l < %(refs)s ) / $( wc -l < %(fCorpus)s ) ))'%inputs)
		commands.append(r'awk "BEGIN{i=0} {print>>(\"separate-reference-files/ref\"i);i+=1;i%=$numRefs}" <'+inputs['refs'])
		
		commands.append('./scripts/training/absolutize_moses_model.pl moses.ini > moses.abs.ini')
		commands.append('(cd mert-work && $dir/scripts/training/mert-moses.pl --rootdir $dir/scripts '+
						' --mertdir $dir/mert --working-dir $dir/mert-work'+
						' --input $dir/%(fCorpus)s --refs $dir/separate-reference-files/ref'%inputs+
						' --decoder $dir/moses-cmd/src/moses --config $dir/moses.abs.ini'+
						noFilter+
						' 2>&1 | tee mert.log)')
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
    
