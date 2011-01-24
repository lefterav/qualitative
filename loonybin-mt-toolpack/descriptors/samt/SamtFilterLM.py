from loonybin import Tool
from HadoopTool import HadoopTool

class SamtFilterLM(Tool):
    
    def __init__(self):
        self.hadoop = HadoopTool()
    
    def getName(self):
        return 'Machine Translation/SAMT/Filter Language Model'
    
    def getDescription(self):
        return """
        TODO
        """
    
    def getRequiredPaths(self):
        return ['samt']

    def getParamNames(self):
        params = self.hadoop.getSharedParams(False)
        params.extend([
                        ('outputBufferLimit','? (default: 1000000)'),
                        ])
        return params
    
    def getInputNames(self, params):
        return [ ('hdfs:unfilteredLM', 'Language Model in ARPA format'),
                 ('hdfs:filteredRules','SAMT-format rules, filtered to the desired test set') ]

    def getOutputNames(self, params):
        return [ ('hdfs:filteredLM','Extracted phrase instances in SAMT format') ]
    
    def getCommands(self, params, inputs, outputs):

        mapper=('"./LMFilter --HdfsInputDir %(hdfs:filteredRules)s '%inputs +
            '--RunningMode 1 --outputbufferlimit %(outputBufferLimit)s"'%params)
        reducer='"./LMFilter --RunningMode 2"'

        return ['hadoop jar $HADOOP_HOME/hadoop-streaming.jar -Dmapred.map.tasks=%(numMapTasks)s -Dmapred.reduce.tasks=%(numReduceTasks)s -Dmapred.job.queue.name=%(queueName)s '%params +
            ' -Dmapred.job.reduce.memory.mb=2048 -Dmapred.job.map.memory.mb=2048 -Dmapred.text.key.partitioner.options=-kn' +
            ' -Dstream.non.zero.exit.is.failure=true -Dmapred.job.name="SAMT Filter LM"' +
            ' -input %(hdfs:unfilteredLM)s'%inputs +
            ' -output %(hdfs:filteredLM)s'%outputs +
            ' -mapper %s'%mapper +
            ' -reducer %s'%reducer +
            ' -file ./O2/LMFilter']
    
    def getPostAnalyzers(self, params, inputs, outputs):
        return [ ]

if __name__ == '__main__':
    import sys
    t = SamtFilterLM()
    t.handle(sys.argv)
