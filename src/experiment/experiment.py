'''
Created on Aug 31, 2011

@author: elav01
'''

class Experiment(object):
    '''
    classdocs
    '''
    input = []
    output = []
    phases = []


    def __init__(self, params):
        '''
        Constructor
        '''
        pass

    def run(self):  
        for phase in self.phases:
            nextinput = phase.input
            for task in phase.tasks:
                if False not in [req.completed for req in task.required]:
                    task.input = nextinput
                    task.run()
                    task.completed = True
                    nextinput = task.output
                
        