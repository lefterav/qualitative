'''
Created on Aug 31, 2011

@author: Eleftherios Avramidis
'''

class Experiment(object):
    '''
    classdocs
    '''
    input = []
    output = []
    phases = []
    completed = False

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self):  
        output = self.input
        for phase in self.phases:
#        for phase in self.phases:
            phase.input = output
            phase.run()
            output = phase.output
        
        self.completed = True
        

    def __get_executable_phases__(self):
        """
        Return a list of the tasks that have all their requirements met
        """
        
        executable_phases = []
        
        for phase in self.phases:
            allcompleted = True
            for requirement in phase.required:
                if not requirement.completed:
                    allcompleted = False
            if allcompleted:
                executable_phases.append(phase)
        
        return executable_phases


#            for task in phase.tass:
#                if False not in [req.completed for req in task.required]:
#                    task.input = nextinput
#                    task.run()
#                    task.completed = True
#                    nextinput = task.output
                
        