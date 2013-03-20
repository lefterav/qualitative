'''
Created on 20 Mar 2013

@author: elav01
'''

class Ranking(object):
    '''
    classdocs
    '''


    def __init__(self, ranking):
        '''
        @param ranking: a list of values representing a ranking
        @type ranking: list of integers or strings
        '''
        self.ranking = ranking
        
    def __getitem__(self, key):
        return self.ranking[key]
    
    def __iter__(self):
        return self.ranking.__iter__() 
    
    def normalized(self, **kwargs):
        '''
        Convert a messy ranking like [1,3,5,4] to [1,2,4,3]
        @keyword inflate_ties: If true count ties, e.g. [1,4,4,3] gets normalized to [1,4,4,2] 
        @type inflate_ties: boolean 
        '''
        inflate_ties = kwargs.setdefault('inflate_ties', True)
        
        
    
    

        
        