'''
Utilize the scikit machine learning library for ranking
Created on Sep 24, 2014

@author: Eleftherios Avramidis
'''
from dataprocessor.ce.cejcml import CEJcmlReader
import numpy as np
from ml.ranking import Ranker
from sklearn.svm import SVC
import logging as log

def dataset_to_instances(filename, 
                         attribute_set=None,
                         class_name=None,
                         reader=CEJcmlReader,  
                         tempdir = "/tmp",
                         output_filename=None,
                         default_value = '',
                         replace_infinite=False,
                         **kwargs):
    """
    Receive a dataset filename and convert it into a memory table for the Orange machine learning
    toolkit. Since we need support for big data sets and optimal memory usage, the best way
    seems to create a temporary external tab separated file and load it directly with the Orange
    loader, which is implemented in C. This way no double object instances need to be on memory
    during conversion time.
    @param attribute_set: A description of the attributes we want to be included in the data table
    @type attribute_set: L{AttributeSet}
    @param class_name: The name of the class (label) for the machine learning task
    @type class_name: C{str}
    @param reader: A class which is able to read from external files. This give the possibility to 
    change the default reading behaviour (incremental XML reader) and read from other types of data files
    @type reader: L{DataReader} 
    @param tempdir: the temporary directory where the incremental file is written. Due to the
    increased I/O access, this is suggested to be in a storage unit that is locally connected to the
    computer that does the processsing, and not e.g. via NFS.
    @type tempdir: C{str}
    @param ouput_filename: specify here a full path if a copy of the Orange tab separated file needs to be
    retained (e.g. for debugging purposes)
    @type output_filename: C{str}
    @return An Orange Table object
    @rtype: C{Table}
    """
    
    
    
    #initialize the class that will take over the reading from the file
    dataset = reader(filename, compact=True, 
                     all_general=True,
                     all_target=True)
    
    features = None
    labels = None
    
    #iterate over all parallel sentences provided by the data reader
    for parallelsentence in dataset.get_parallelsentences():
        vectors = parallelsentence.get_vectors(attribute_set, 
                                               class_name=class_name, 
                                               default_value=default_value,
                                               replace_infinite=replace_infinite,
                                               )
        
        #every parallelsentence has many instances
        featurevectors = []
        class_values = []
        
        #create a temporary python array for the new vectors
        for featurevector, class_value in vectors:
            featurevectors.append(np.array(featurevector))
            class_values.append(np.array([class_value]))
        
        #convert to numpy
        newfeatures = np.array(featurevectors)
        newlabels = np.array(class_values)
        
        #append them to existing vectors if there are
        try:
            features = np.concatenate((features, newfeatures), axis=0)
            labels = np.concatenate((labels, newlabels), axis=0)
        except ValueError:
            #or initialize the total vectors
            features = newfeatures
            labels = newlabels
            
    return features, labels


class SkRanker(Ranker):
    '''
    Basic ranker wrapping scikit-learn functions
    '''
    
    def train(self, dataset_filename, optimize=True, **kwargs):
        data, labels = dataset_to_instances(filename=dataset_filename, **kwargs)
        learner = eval(self.learner) 
        
        
        if optimize:
            self.learner = optimize_model(self.learner(), data, labels, )
        else:
            self.learner = learner(**kwargs)
        
        self.classifier = self.learner.fit(data, labels)
        self.fit = True


def optimize_model(estimator, X_train, y_train, params, scores, folds, verbose, n_jobs):
    clf = None
    for score_name, score_func in scores:
        log.info("Tuning hyper-parameters for %s" % score_name)
        
        log.debug(params)
        log.debug(scores)
        
        clf = GridSearchCV(estimator, params, loss_func=score_func, 
                           cv=folds, verbose=verbose, n_jobs=n_jobs)
        
        clf.fit(X_train, y_train)
        
        log.info("Best parameters set found on development set:")
        log.info(clf.best_params_)
        
    return clf.best_estimator_
        