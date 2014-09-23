'''
Created on 26 Mar 2013

@author: Eleftherios Avramidis
'''
from sentence.pairwisedataset import pairwise_ondisk
import os
import cPickle as pickle
from dataprocessor.ce.utils import join_jcml 

class PairwiseRanker():
    '''
    classdocs
    '''
    
    def __init__(self, classifier=None, filename=None, learner=None):
        self.fit = True
        if classifier:
            self.classifier = classifier
        elif filename:
            classifier_file = open(filename)
            self.classifier = pickle.load(filename)
            classifier_file.close()
        else:
            self.learner = learner
            self.fit = False
    
    def train(self, dataset_filename, **kwargs):
        pairwise_dataset_filename = dataset_filename.replace(".jcml", ".pair.jcml")
        pairwise_ondisk(dataset_filename, pairwise_dataset_filename, **kwargs)
        super(PairwiseRanker, self).train(pairwise_dataset_filename)
        #self.classifier = PairwiseRanker(classifier=pairwise_classifier)
      
    
    def rank(self, parallelsentence):
        
        pass
