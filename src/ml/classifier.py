'''
It provides a general classifier API which unifies common 
machine learning functions

Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''
from ml.lib import orange


def forname(name, library='orange', **kwargs):
    """ 
    Wrap the specified external classifier into the generic
    classifier class and return the object
    @param name: the name of the classifier
    @param library: the name of the library whose classifeir should be used
    """  
    if library=='orange':
        return orange.forname(name, **kwargs)
    



class Classifier(object):
    '''
    classdocs
    '''


    def __init__(self, object):
        '''
        Constructor
        '''
        pass