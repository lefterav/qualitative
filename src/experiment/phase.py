'''
Created on Aug 31, 2011

@author: elav01
'''

class Phase(object):
    '''
    classdocs
    '''
    input = ""
    output = ""
    tasks = []
    name = ""
    completed = False

    def __init__(self):        
        '''
        Constructor
        '''
    
    def run(self):
#        raise Exception("Unimplemented abstract method")
        torun = [self.tasks[i] for i in range(len(self.tasks)) if self.tasks[i].is_ready()]
        
        while torun:
            for task in torun:
                
                task.input = self.input
                task.run()
                self.output = task.output
            torun = [self.tasks[i] for i in range(len(self.tasks)) if self.tasks[i].is_ready()]
            
        self.completed = True
            
    
    def __get_executable_tasks__(self):
        """
        Return a list of the tasks that have all their requirements met
        """
        
        executable_tasks = []
        
        for task in self.tasks:
            allcompleted = True
            for requirement in task.required:
                if not requirement.completed:
                    allcompleted = False
            if allcompleted:
                executable_tasks.append(task)
        
        return executable_tasks
                    
    
        