'''
Created on Aug 25, 2017

@author: Eleftherios Avramidis
'''

class Scorer(object):
    '''
    Abstract class for a real number predictor
    (also referred to as a Regressor)
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def score(self, featurevector):
        raise NotImplementedError