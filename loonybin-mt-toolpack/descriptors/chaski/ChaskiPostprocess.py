from loonybin import Tool

class Combine(Tool):
    
    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Separate Tables (Postprocessing)'
    
    def getDescription(self):
        return "Generate Moses-compatible phrase table and reorder table"
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        return [ ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue') ]
    
    def getInputNames(self, params):
        return [ ('hdfs:combinedTable','') ]

    def getOutputNames(self, params):
        return [ ('hdfs:mosesPhraseTable', 'Output path of Moses compatible phrase table'),
                 ('hdfs:mosesReorderTable','Output path of Moses compatible reorder table') ]
    
    def getCommands(self, params, inputs, outputs):
        paramString = ' '.join('--%s %s'%(key,value) for (key,value) in params.iteritems())
        cmd = ('hadoop jar chaski-0.0-latest.jar postproc --overwrite true --ptable %(hdfs:)s/combinedTable'%outputs+
               ' --moses-p %(hdfs:mosesPhraseTable)s --moses-r %(hdfs:mosesReorderTable)s '%outputs+
               paramString )
        return ['hadoop dfs -cp %(hdfs:combinedTable)s '%inputs + '%(hdfs:)s/combinedTable'%outputs,
                cmd]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Combine()
    t.handle(sys.argv)
