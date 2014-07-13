'''
It provides a general classifier API which unifies common 
machine learning functions

Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''



def forname(name, library='orange', **kwargs):
    """ 
    Wrap the specified external classifier into the generic
    classifier class and return the object
    @param name: the name of the classifier
    @param library: the name of the library whose classifeir should be used
    """  
    pass
    


class Regressor(object):
    def __init__(self, object):
        pass
    
    def load_training_dataset(self, dataset,
                         class_name,
                         desired_parallel_attributes = [],
                         desired_source_attributes = [],
                         desired_target_attributes = [],
                         meta_attributes = [],
                         scale=True):
        raise NotImplementedError();
    
    def feature_selection(self, config):
        raise NotImplementedError();

        
    def set_learning_method(self, config):
        raise NotImplementedError();
    
    
    def cross_validate_scores(self):
        if not self.training_data_loaded:
            raise AssertionError("Training data must be loaded, before cross validation")
        self.cross_validate_start();
    
    def train(self):
        self.train_start(self)
    
    def test_dataset(self):
        raise NotImplementedError();
    
    def predict_dataset(self):
        raise NotImplementedError();


class Classifier(object):
    '''
    classdocs
    '''


    def __init__(self, object):
        '''
        Constructor
        '''
        pass
