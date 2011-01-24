from loonybin import Tool
from Cdec import Cdec

class CdecMert(Tool):
    
    def __init__(self):
        self.decoder = Cdec()
    
    def getName(self):
        return 'Machine Translation/Tuning/Cdec MERT (VEST)'
    
    def getDescription(self):
        return "Tunes a translation system, decoding with Cdec and using Cdec's hypergraph MERT"
    
    def getRequiredPaths(self):
        return ['cdec']

    def getParamNames(self):
        params = self.decoder.getSharedParams()
	params.append( ('metric','Metric to be used as an objective function (IBM_BLEU, NIST_BLEU, Koehn_BLEU, TER, Combi)') )
	params.append( ('pmem','Amount of physical memory to request for each decoder instance') )
        return params

    def getInputNames(self, params):
        inputs = self.decoder.getSharedInputs(params)
        inputs.extend([ ('fCorpus', 'tokenized "foreign" sentences on which we will tune, one sentence per line'),
                        ('refs', 'tokenized interlaced references, one reference sentence per line with references for one source sentence followed immediately by all references for the next source sentence'),
                        ('initialWeights','Cdec-format weights file containing initial weights for features') ])
        return inputs

    def getOutputNames(self, params):
        return [ ('optimizedWeightsFile','Cdec-format weights file with best weights found by optimizer'),
		 ('finalTopbest','Topbest hypotheses from final iteration of MERT, one sentence per line') ]
    
    def getCommands(self, params, inputs, outputs):

		# Create base cdec.ini on the fly
	        # TODO: Make running locally an option
		commands = self.decoder.makeConfigFileCommands(params, inputs, 'cdec.ini')

		# Unpack references from single file into multiple files
		# with the prefix $dir/separate-reference-files/ref
		# and ending with ...ref0, ...ref1, etc
	        # TODO: Share this code with moses instead of using abject-oriented inheritance
		commands.append('mkdir separate-reference-files')
                commands.append('numRefs=$(( $( wc -l < %(refs)s ) / $( wc -l < %(fCorpus)s ) ))'%inputs)
		commands.append(r'awk "BEGIN{i=0} {print>>(\"separate-reference-files/ref\"i);i+=1;i%=$numRefs}" <'+inputs['refs'])

		commands.append('./vest/dist-vest.pl --workdir vest-work --pmem %(pmem)s'%params+
			        " --source-file %(fCorpus)s --ref-files $(pwd)/'separate-reference-files/ref*' --weights %(initialWeights)s cdec.ini 2>&1 | tee vest.log"%inputs)
		
		commands.append('finalTopbestGz=$(ls -t vest-work/run.raw.*.gz | head -1)')
		commands.append('zcat $finalTopbestGz > %(finalTopbest)s'%outputs)
		
		commands.append('finalWeights=$(ls -t vest-work/weights.* | head -1)')
		commands.append('cp $finalWeights %(optimizedWeightsFile)s'%outputs)

		return commands
    
    def getPreAnalyzers(self, params, inputs):
        # TODO: Log entire config file
        # TODO: Make sure we don't have any blank inputs
        return [ ]

    def getPostAnalyzers(self, params, inputs, outputs):
        # TODO: Make sure we have the same number of output hypotheses as inputs
        #cmd = ('extract_zmert_stats.pl zmert.stdout %(paramConfigFile)s'%inputs)
        return [ ]

    def getStatus(self, params, inputs):
        return [ "egrep -o '^ITERATION [0-9]+' vest.log | tail -n 1",
                 "egrep -ho '^BLEU = [0-9.]+' vest.log | tail -n 1",
		 "fgrep 'OPT-ITERATION' vest.log | tail -n 1" ]

if __name__ == '__main__':
    import sys
    t = CdecMert()
    t.handle(sys.argv)
    
