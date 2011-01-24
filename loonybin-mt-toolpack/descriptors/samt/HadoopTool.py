from loonybin import Tool

class HadoopTool:
    
    def getSharedParams(self, mapperOnly):
        params = [ ('queueName','?'),
                   ('numMapTasks', '?') ]
        params.extend([
                       ('numReduceTasks','?')
                       ])
        return params
