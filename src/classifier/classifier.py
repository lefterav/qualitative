"""

@author: Eleftherios Avramidis
"""
    
import Orange
from Orange.data import Table
from Orange.classification import Classifier

class OrangeClassifier():
    """
    Base function encapsulated common functions for all classifier subclasses
    """
    
    def __init__(self, classifier):
        self.classifier = classifier
        
        
    def classify_orange_table(self, orange_table, return_type=Classifier.GetBoth):
        #orange_table = Table()
        resultvector = []
        for instance in orange_table:
            value, distribution = self.classifier.__call__(instance, return_type)
            resultvector.append((value.value, distribution))
        return resultvector 
            

    def classify_dataset(self, dataset, return_type=Classifier.GetBoth):
        pass
    
    def classify_parallelsentence(self, parallelsentence, return_type=Classifier.GetBoth):
        pass

#    def __call__(self, data):
#        return self.classifier.__call__(data)
#        
#    def getFilteredLearner(self, n=5):
#        return orngFSS.FilteredLearner(self, filter=orngFSS.FilterBestNAtts(n), name='%s_filtered' % self.name)

