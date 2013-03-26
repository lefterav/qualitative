'''
This module should be connecting classifier wrappers with the external Machine Learning classification libraries.

Created on 26 Mar 2013

@author: Eleftherios Avramidis
'''

def get_classifier(library_name, classifier_name):
    """
    This function looks up the requested classifiers in the external mac and returns a wrapped classifier object
    """
    pass

class AbstractClassifier(object):
    def __init__(self, **kwargs):
        pass
    
    def train(self, **kwargs):
        pass
    
    def decode(self, **kwargs):