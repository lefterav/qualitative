'''
Created on Aug 31, 2011

@author: elav01
'''

import sys

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
        for task in self.final_tasks:
            self.check_run(task)
        
    
    def check_run(self, task):
        if not task.is_ready():
            prerequisites = self.task.get_pending_prerequisites()
            for prerequisite in prerequisites:
                self.check_run(prerequisite)
            sys.stderr.write("runining task %s"% task.name)
            task.run()
            
        else:
            sys.stderr.write("task %s has already finished"% task.name)
            
        
    
#    def run(self):
#        
##        raise Exception("Unimplemented abstract method")
#        torun = [task for task in self.tasks if task.is_ready() and not task.completed]
#        
#        while torun:
#            for task in torun:
#                
#                task.input = self.input
#                task.run()
#                self.output = task.output
#            torun = [task for task in self.tasks if task.is_ready() and not task.completed]
#            
#        self.completed = True
#            
#    
#    def __get_executable_tasks__(self):
#        """
#        Return a list of the tasks that have all their requirements met
#        """
#        
#        executable_tasks = []
#        
#        for task in self.tasks:
#            allcompleted = True
#            for requirement in task.required:
#                if not requirement.completed:
#                    allcompleted = False
#            if allcompleted:
#                executable_tasks.append(task)
#        
#        return executable_tasks
#                    
    
        