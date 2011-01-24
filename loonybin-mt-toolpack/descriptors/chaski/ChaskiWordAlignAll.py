from loonybin import Tool

# put Mgiza.py on the path and then import it
import sys
scriptDir = sys.path[0]
sys.path.append(scriptDir+'/../wordalign')
from Mgiza import Mgiza

class Chaski(Tool):
	
    def __init__(self):
        # TODO: Only provide parameters from relevant models
        self.mgiza = Mgiza('A', True)

    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Word Alignment'
    
    def getDescription(self):
        return "Run parallel word alignment"
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        # TODO: Force filtering to be in a separate tool!
        # Hidden: verbose, maxsl
        # TODO: Expose all giza params here?
        params = [ ('train', 'The training sequence, 1 for model 1, H for HMM, 3 for model 3, 4 for model 4, * to normalize'),
                 ('direction', 'The direction of alignment, by default it is 3 which means both s2t and t2s, specify 1 for s2t only and 2 for t2s only, 0 for merging alignments only'),
                 ('symalmethod', 'Symmetrization heuristic'),
                 ('num-reducer', 'Total number of available reducer slots'),
                 ('mgiza-root', 'The directory where mgiza installed (should be accessible on the cluster)'),
                 ('memorylimit', ' The amount of memory that can be used every time, this will affect how many splits we have. The unit is MB'),
                 ('highcocurrency', 'Whether the driver will seek to parallize as much as possible, for example, normalize different tables in parallel'),
                 ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue with default queue (m45)'),
                 ('score.mb','Number of megabyes to use in scoring (reduce if OutOfMemory Exception; default 2000000)'),
                 ('score.cc','Use compact cache so that we can keep more in memory during scoring without getting an OutOfMemory Exception (true/false)')
                 ]
        
        for (name, desc, default, when) in self.mgiza.possibleParams:
			if self.mgiza.appliesToModel(self.mgiza.mode, when):
				params.append( ('giza.'+name, desc, default) ) 
        return params
    
    def getInputNames(self, params):
        return [ ('hdfs:preppedData', 'Preprocessed corpus file and necessary vocabulary and word cluster files')  ]

    def getOutputNames(self, params):
        return [ ('hdfs:alignedCorpus', 'Aligned corpus that can be directly used in phrase extraction') ]
    
    def getCommands(self, params, inputs, outputs):
		groot = params['mgiza-root'];
		params["giza"] = groot + '/bin/mgiza';
		params["hmmnorm"] = groot + '/bin/hmmnorm';
		params["d4norm"] = groot + '/bin/d4norm';
		params["symalbin"] = groot + '/bin/symal';
		params["symalscript"] = groot + '/scripts/symal.sh';
		params["giza2bal"] = groot + '/scripts/giza2bal.pl';
		paramString = ' '.join('--%s %s' % (key, value) for (key, value) in params.iteritems())
		# TODO: distributable tarball?
		
		rmCmd = 'rm -rf tmp'
		copyCmd = 'hadoop dfs -cp %(hdfs:preppedData)s ' % inputs + ' %(hdfs:)s' % outputs
		runCmd = ('hadoop jar chaski-0.0-latest.jar walign --overwrite true --root %(hdfs:)s ' % outputs + 
				paramString +
				' --output %(hdfs:alignedCorpus)s' % outputs)      
		return [ rmCmd, copyCmd, runCmd ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Chaski()
    t.handle(sys.argv)
