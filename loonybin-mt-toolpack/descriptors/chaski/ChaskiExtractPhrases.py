from loonybin import Tool

class Combine(Tool):
    
    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Extract Phrases'
    
    def getDescription(self):
        return "Extract phrase pairs and count the occurrences in the corpus"
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        return [ ('max-phrase-len','Maximum phrase length, default is 7'),
                 ('num-mapper', 'Total number of available mapper slots'),
                 ('num-reducer', 'Total number of available reducer slots'),
                 ('map-per-node','Number of mappers per node, it may be ignored if your cluster does not allow you to change it'),
				 ('red-per-node','Number of reducers per node, it may be ignored if your cluster does not allow you to change it'),
                 ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue'),
                 ('heap', 'Specify how much memory should each children task (Map/Reduce) use, default is 1024m'),
                 ]
    
    def getInputNames(self, params):
        return [ ('hdfs:alignedCorpus','Aligned corpus output by word alignment') ]

    def getOutputNames(self, params):
        return [ ('hdfs:extractedPhrases', 'Output phrase count file, contains phrase pairs and their occurrences in the corpus') ]
    
    def getCommands(self, params, inputs, outputs):
        paramString = ' '.join('--%s %s'%(key,value) for (key,value) in params.iteritems())
        cmd = ('hadoop jar chaski-0.0-latest.jar extract --overwrite true --corpus %(hdfs:)s '%outputs+
                 ' --phrase %(hdfs:extractedPhrases)s '%outputs+
                 paramString)
        return ['hadoop dfs -cp %(hdfs:alignedCorpus)s '%inputs + '%(hdfs:)s'%outputs,
                cmd]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Combine()
    t.handle(sys.argv)
