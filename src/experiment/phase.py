'''
Created on Aug 31, 2011

@author: elav01
'''

class Phase(object):
    '''
    classdocs
    '''
    input = []
    otuput = []
    tasks = []
    name = ""

    def __init__(self, params):        
        '''
        Constructor
        '''
    
    def run(self):
        raise Exception("Unimplemented abstract method") 
    
        