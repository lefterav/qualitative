from loonybin import Tool
from HadoopTool import HadoopTool

class SamtExtractPhrases(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
    
    def getName(self):
        return 'Machine Translation/SAMT/Extract Phrases'
    
    def getDescription(self):
        return """
        Extracts phrases using the Koehn heuristics.
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        params = self.hadoop.getSharedParams(True)
        params.extend([
                        ('maxPhraseLength','?')
                        ])
        return params
    
    def getInputNames(self, params):
        return [ ('hdfs:combinedSentenceData','?') ]

    def getOutputNames(self, params):
        return [ ('hdfs:phraseInstances','Extracted phrase instances in SAMT format') ]
    
    def getCommands(self, params, inputs, outputs):
            return ['hadoop jar $HADOOP_HOME/hadoop-streaming.jar -Dmapred.map.tasks=%(numMapTasks)s -Dmapred.reduce.tasks=0 -Dmapred.job.queue.name=%(queueName)s'%params +
                        ' -Dstream.non.zero.exit.is.failure=true -Dmapred.job.name="SAMT Extract Phrases"' +
                        ' -input %(hdfs:combinedSentenceData)s '%inputs +
                        ' -mapper "./MapExtractPhrases %(maxPhraseLength)s"'%params +
                        ' -file ./O2/MapExtractPhrases -output %(hdfs:phraseInstances)s'%outputs ]
            
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtExtractPhrases()
    t.handle(sys.argv)
