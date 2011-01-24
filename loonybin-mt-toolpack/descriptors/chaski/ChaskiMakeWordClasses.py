from loonybin import Tool

class MakeWordClasses(Tool):
    
    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Make Word Classes'
    
    def getDescription(self):
        return """Makes word classes in a DIFFERENT way than Och's mkcls. Filters will also be applied on input corpus.
The model we used is "One-side" class-based model, in contrast to "Two-side" class-based model in mkcls"""
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        # TODO: Force filtering to be in a separate tool!
        # Hidden: verbose, maxsl
        return [ ('num-reducer', 'Total number of available reducer slots'),
                 ('num-iter', 'Total number of iterations'),
                 ('num-classes', 'Total number of classes'),
                 ('class-side', 'The direction of class, by default it is 2 which means both s2t and t2s, specify 0 for s2t only and 1 for t2s only'),
                 ('heap', 'Specify how much memory should each children task (Map/Reduce) use, default is 1024m'),
                 ('highcocurrency', 'Whether the driver will seek to parallize as much as possible, for example, normalize different tables in parallel'),
                 ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue')
                 ]
    
    def getInputNames(self, params):
        return [ ('hdfs:srcCorpus','Source corpus file'),
                 ('hdfs:tgtCorpus','Target corpus file') ]

    def getOutputNames(self, params):
        return [ ('hdfs:srcClasses', 'Source vocabulary with word class assigned to each entry'),
                 ('hdfs:tgtClasses', 'Target vocabulary with word class assigned to each entry') ]
    
    def getCommands(self, params, inputs, outputs):
        heap = params["heap"].lower();
        if len(heap)>0 and heap[-1]!='m' and heap[-1]!='g':
           heap = heap + "m";
        params["heap"] = heap;
        paramString = ' '.join('--%s %s'%(key,value) for (key,value) in params.iteritems())
        
        # We essentially do not limit the source length here since we would prefer that be done as a separate step
        # These appear to do nothing for mkcls... --src %(hdfs:srcCorpus)s --tgt %(hdfs:tgtCorpus)s'%inputs+
        cmd = ('hadoop jar chaski-0.0-latest.jar mkcls --overwrite false --src dummyFile --tgt dummyFile' +
                ' --root %(hdfs:)s --filter-log path --nocopy --maxsl 99999 '%outputs +
                paramString)
        
        # the key "hdfs:" in the outputs dict tells us the HDFS root directory for outputs
        return [ 'hadoop dfs -cp %(hdfs:srcCorpus)s'%inputs + ' %(hdfs:)s/src-raw-corpus'%outputs,
                 'hadoop dfs -cp %(hdfs:tgtCorpus)s'%inputs + ' %(hdfs:)s/tgt-raw-corpus'%outputs,
                 cmd,
                 'hadoop dfs -mv %(hdfs:)s/dict/src.classes %(hdfs:srcClasses)s'%outputs,
                 'hadoop dfs -mv %(hdfs:)s/dict/tgt.classes %(hdfs:tgtClasses)s'%outputs ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = MakeWordClasses()
    t.handle(sys.argv)
