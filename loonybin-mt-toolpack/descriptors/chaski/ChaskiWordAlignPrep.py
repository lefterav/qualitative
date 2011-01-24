from loonybin import Tool

class Combine(Tool):
    
    def getName(self):
        return 'Machine Translation/Grammars and Tables/Chaski (Hadoop)/Word Align Prep'
    
    def getDescription(self):
        return "Prepare corpus for distributed word alignment"
    
    def getRequiredPaths(self):
        return ['chaski']

    def getParamNames(self):
        # TODO: Force filtering to be in a separate tool!
        # Hidden: verbose, maxsl
        return [ ('num-reducer', 'Total number of available reducer slots'),
                 ('memorylimit', ' The amount of memory that can be used every time, this will affect how many splits we have. The unit is MB'),
                 ('queues', 'Specify the queue that the MR-Job will be submitted, if not specified, a warning will be displayed but the execution will continue with default value "(M45)"')
                 ]
    
    def getInputNames(self, params):
        return [ ('hdfs:srcCorpus','Source corpus file'),
                 ('hdfs:tgtCorpus','Target corpus file'),
				 ('srcClasses','Source class file'),
				 ('tgtClasses','Target class file') ]

    def getOutputNames(self, params):
        return [ ('hdfs:preppedData', 'The root directory for word alignment') ]
    
    def getCommands(self, params, inputs, outputs):
        
        paramString = ' '.join('--%s %s'%(key,value) for (key,value) in params.iteritems())
        # TODO: distributable tarball?
        cmd = ('hadoop jar chaski-0.0-latest.jar waprep --overwrite true --maxsl 99999 ' +
                ' --source %(hdfs:srcCorpus)s --target %(hdfs:tgtCorpus)s '%inputs+
				' --srcclass %(srcClasses)s --tgtclass %(tgtClasses)s '%inputs+
                paramString+
                ' --root %(hdfs:preppedData)s'%outputs)
        
        return [cmd ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = Combine()
    t.handle(sys.argv)
