"""

@author: Eleftherios Avramidis
"""
    
import orngFSS

class OrangeClassifier(object):
    """
    Base function encapsulated common functions for all classifier subclasses
    """

    def __call__(self, data):
        return self.classifier.__call__(data)
        
    def getFilteredLearner(self, n=5):
        return orngFSS.FilteredLearner(self, filter=orngFSS.FilterBestNAtts(n), name='%s_filtered' % self.name)