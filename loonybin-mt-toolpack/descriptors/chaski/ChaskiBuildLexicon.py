from loonybin import Tool

class Combine(Tool):
    
    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Build Lexicon'
    
    def getDescription(self):
        return "Build lexicon from (symetrized) word alignments"
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        return [ ('num-mapper', 'Total number of available mapper slots'),
                 ('num-reducer', 'Total number of available reducer slots'),
                 ('parallel', 'Whether the driver will seek to parallize as much as possible, for example, normalize different tables in parallel'),
                 ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue')
                 ]
    
    def getInputNames(self, params):
        return [ ('hdfs:alignedCorpus','Aligned corpus') ]

    def getOutputNames(self, params):
        return [ ('hdfs:lexicon', 'The output lexicon file') ]
    
    def getCommands(self, params, inputs, outputs):
        
        paramString = ' '.join('--%s %s'%(key,value) for (key,value) in params.iteritems())
        cmd = ('hadoop jar chaski-0.0-latest.jar buildlex --overwrite false --corpus %(hdfs:)s '%outputs+
                 ' --lexicon %(hdfs:lexicon)s '%outputs+
                 paramString)
        
        return ['hadoop dfs -cp %(hdfs:alignedCorpus)s '%inputs + '%(hdfs:)s'%outputs,
                cmd]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Combine()
    t.handle(sys.argv)
