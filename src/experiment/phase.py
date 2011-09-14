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
        torun = [task for task in self.tasks if task.is_ready() and not task.completed]
        
        while torun:
            for task in torun:
                
                task.input = self.input
                task.run()
                self.output = task.output
            torun = [task for task in self.tasks if task.is_ready() and not task.completed]
            
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
                    
    
        