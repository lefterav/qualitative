'''
Created on 04 Mar 2012
@author: lefterav
'''

from Orange.regression.linear import LinearRegressionLearner 
from Orange.regression.pls import PLSRegressionLearner
from Orange.regression.lasso import LassoRegressionLearner
from Orange.regression.earth import EarthLearner
from Orange.regression.tree import TreeLearner

from Orange.classification.knn import kNNLearner
from Orange.classification.bayes import NaiveLearner
from Orange.classification.svm import SVMLearnerEasy as SVMEasyLearner
#from classifier.svmeasy import SVMEasyLearner
from Orange.classification.tree import TreeLearner
from Orange.classification.logreg import LogRegLearner

from io_utils.input.jcmlreader import JcmlReader
#from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.sax.saxjcml2orange import SaxJcml2Orange
from classifier.classifier import OrangeClassifier
from Orange.data import Table


import sys
import shutil
import cPickle as pickle
import os

from expsuite import PyExperimentSuite



class QualityEstimationSuite(PyExperimentSuite):
    
    def reset(self, params, rep):
        self.restore_supported = True
        classifier_name = params["classifier"] + "Learner"
        try:
            self.classifier_params = eval(params["params_%s" % params["classifier"]])
        except:
            self.classifier_params = {}
        self.learner = eval(classifier_name)
        self.meta_attributes = params["meta_attributes"].split(",")
        self.active_attributes = params[params["att"]].split(",")
        if self.active_attributes == [""]:
            self.active_attributes = []
        self.discretization = False
        if params["discretization"]:
            self.discretization = params["discretization"]
        self.hidden_attributes = params["hidden_attributes"].split(",")
        self.discrete_attributes = params["discrete_attributes"].split(",")
        self.class_name = params["class_name"]
        self.class_type = params["class_type"]
    
    def iterate(self, params, rep, n):
        ret = {}
        
        print "experiment", os.getcwd()
        print "iteration", n
        if n == 1:
            print "loading big set"
            shutil.copy(params["training_set"], "trainset.jcml")
        if n == 2:
            self._get_testset(params["test_set"], params["mode"])
            
     
        if n == 3:
            print "converting to orange"
            SaxJcml2Orange("trainset.jcml", 
                 self.class_name,
                 self.active_attributes, 
                 self.meta_attributes, 
                 "trainset.tab", 
                 compact_mode = True, 
                 discrete_attributes=self.discrete_attributes,
                 hidden_attributes=self.hidden_attributes,
                 get_nested_attributes=True,
                 #filter_attributes={"rank" : "0"},
                 class_type=self.class_type,
                 class_discretize = self.discretization
                                         )

        if n == 4:
            orangeData = Table("trainset.tab")
            mylearner = self.learner(**self.classifier_params) #imputer=self.imputer)
            self.myclassifier = OrangeClassifier(mylearner(orangeData))
        if n == 5:
            self.meta_attributes.append(self.class_name)
            print "orange version of test set"
            SaxJcml2Orange("testset.jcml", "", 
                                                 self.active_attributes, 
                                                 self.meta_attributes, 
                                                 "testset.tab", 
                                                 compact_mode=True, 
                                                 discrete_attributes=self.discrete_attributes,
                                                 hidden_attributes=self.hidden_attributes, 
                                                 get_nested_attributes=True
                                                 )
        if n == 6:
            print "performing classification"
            orangeData = Table("testset.tab")
            classified_set_vector = self.myclassifier.classify_orange_table(orangeData)
            self.classified_values_vector = [str(v[0]) for v in classified_set_vector]
#            print classified_set_vector
        
        if n == 7:
            print "EVALUATION"
            print "reloading test set"
            self.simple_testset = JcmlReader("testset.jcml").get_dataset()
            
            print "adding attribute vector"
            att_vector = [{"score_predicted": v} for v in self.classified_values_vector]
            print att_vector
            self.simple_testset.add_attribute_vector(att_vector, "ps")
            
        
        if n == 8:
            from support.evaluation.wmt12.wmt_scoring import WmtScoring
            ret = WmtScoring(self.simple_testset).process("tgt-1_score", "", "score_predicted", "")
            print ret
            print "finished"
        return ret
        
    def save_state(self, params, rep, n):
        if n == 4:
            objectfile = open("classifier.pickle", 'w')
            pickle.dump(self.myclassifier.classifier, objectfile)
            objectfile.close()
        if n == 6:
            classified_vector_file = open("classified.txt", 'w')
            classified_vector_file.writelines(self.classified_values_vector)
            classified_vector_file.close()
        if n == 7:
            Parallelsentence2Jcml(self.simple_testset).write_to_file("testset.classified.jcml")

    def restore_state(self,params, rep, n):
        if n in [5, 6]:
            objectfile = open("classifier.pickle", 'r')
            self.myclassifier = pickle.load(objectfile)
            objectfile.close()
        if n == 7:
            classified_vector_file = open("classified.txt", 'r') 
            self.classified_set_vector = classified_vector_file.readlines()
            classified_vector_file.close()
        if n == 8:
            self.simple_testset = JcmlReader("testset.classified.jcml").get_dataset
        pass
    ##############################
                
    def _get_testset(self, test_filename, mode = ""):
        if not test_filename == "":
            print "arbitrarily split given set to training and test sets 90% + 10%"
            simple_trainset = JcmlReader("trainset.jcml").get_dataset()
            
            if mode == "development":
                simple_trainset, a = simple_trainset.split(0.1)
            
            simple_trainset, simple_testset = simple_trainset.split(0.7)
            Parallelsentence2Jcml(simple_trainset).write_to_file("trainset.jcml")
            Parallelsentence2Jcml(simple_testset).write_to_file("testset.jcml")
        else:
            shutil.copy(test_filename, "testset.jcml")

if __name__ == '__main__':
    mysuite = QualityEstimationSuite();
    mysuite.start()
    