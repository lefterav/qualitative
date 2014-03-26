'''
Created on 25 Mar 2014

@author: Eleftherios Avramidis
'''
import numpy as np
from ml.learner import Regressor
from learn_model import set_learning_method, set_selection_method, scale_datasets_crossvalidation
from sklearn import cross_validation
import logging as log

def dataset_to_instances(dataset, 
                         class_name,
                         desired_parallel_attributes = [],
                         desired_source_attributes = [],
                         desired_target_attributes = [],
                         meta_attributes = []):
    
    att_table = []
    class_vector = []
    for parallelsentence in dataset:
        att_row = []
        for att_name in desired_parallel_attributes:
            att_value = parallelsentence.get_attribute(att_name)
            if att_name == class_name:
                class_vector.append(float(att_value))
            else:
                att_row.append(float(att_value))
                
        for att_name in desired_source_attributes:
            att_value = parallelsentence.get_source().get_attribute(att_name)
            if att_name == class_name:
                class_vector.append(float(att_value))
            else:
                att_row.append(float(att_value))
        
        for att_name in desired_target_attributes:
            att_value = parallelsentence.get_source().get_attribute(att_name)
            if att_name == class_name:
                class_vector.append(float(att_value))
            else:
                att_row.append(float(att_value))
                
        att_table.append(att_row)
    

    
    numpy_att_table = np.asarray(att_table)
    numpy_class_vector = np.asarray(class_vector)

    if len(numpy_att_table.shape) != 2:
        raise IOError("the training dataset must be in the format of a matrix with M lines and N columns.")
        
    if numpy_att_table.shape[0] != numpy_class_vector.shape[0]:
        raise IOError("the number of instances in the train features file does not match the number of references given.")
    
    return numpy_att_table, numpy_class_vector




        
        
class SkRegressor(Regressor):
    def __init__(self, config=None):
        self.config = config
        
    
    def load_training_dataset(self, dataset,
                         class_name,
                         desired_parallel_attributes = [],
                         desired_source_attributes = [],
                         desired_target_attributes = [],
                         meta_attributes = [],
                         scale=True):
        
        self.X_train, self.Y_train = dataset_to_instances(dataset, 
                         class_name,
                         desired_parallel_attributes,
                         desired_source_attributes,
                         desired_target_attributes,
                         meta_attributes)
        
        if scale:
            self.X_train = scale_datasets_crossvalidation(self.X_train)
        
    
    def feature_selection(self):
        config = self.config
        # sets the selection method
        transformer = set_selection_method(config)
    
        # if the system is configured to run feature selection
        # runs it and modifies the datasets to the new dimensions
        if transformer is not None:
            log.info("Running feature selection %s" % str(transformer))
            log.debug("X_train dimensions before fit_transform(): %s,%s" % self.X_train.shape)
            log.debug("y_train dimensions before fit_transform(): %s" % self.y_train.shape)
            
            X_train = transformer.fit_transform(self.X_train, self.y_train)
            
            log.debug("Dimensions after fit_transform(): %s,%s" % X_train.shape)
        
        
    def set_learning_method(self):
        self.estimator, self.scorers = set_learning_method(self.config, self.X_train, self.y_train)
    
    
    def cross_validate_start(self, cv=10):
        log.info("Running cross validator with %s" % str(self.estimator))
        scores = cross_validation.cross_val_score(self.estimator, self.X_train, self.y_train, cv=cv, scoring=self.scorers)
        return scores
        

    
        
        
    
        
        
    