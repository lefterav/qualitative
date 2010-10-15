'''
Created on 15 Οκτ 2010

@author: elav01
'''

class ParallelSentence(object):
    '''
    classdocs
    '''
    

    def __init__(self, source, translations, reference = ""):
        '''
        Constructor
        @param source The source text of the parallel sentence
        @param translations A list of given translations 
        @param reference The desired translation provided by the system
        '''
        self.src = source
        self.tgt = translations
        self.ref = reference
        
    def get_source(self):
        return self.src
    
    def get_translations(self):
        return self.tgt
    
    def get_reference(self):
        return self.ref

        