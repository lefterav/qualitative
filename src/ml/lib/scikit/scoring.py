'''
Created on Aug 17, 2017

@author: lefterav
'''

from ml.scoring import Scorer

class PreloadedSkScorer(Scorer):
    '''
    This is a generic scorer that loads a model from a file and is capable of scoring based on it   
    '''

    def __init__(self, model):
        if model:
            self.model = model
        
    def score(self, featurevector):
        return self.model.predict(featurevector)