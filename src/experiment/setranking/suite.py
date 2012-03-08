'''
Created on 07 Mar 2012
@author: lefterav
'''
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk

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


import time

import random
import sys
import shutil
import cPickle as pickle
import os

from expsuite import PyExperimentSuite



class QualityEstimationSuite(PyExperimentSuite):
    restore_supported = True
    
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
        if params.has_key("discretization"):
            self.discretization = params["discretization"]
        self.testset_ratio = 0.7
        if params.has_key("testset_ratio"):
            self.testset_ratio = params["testset_ratio"]
        self.hidden_attributes = params["hidden_attributes"].split(",")
        self.discrete_attributes = params["discrete_attributes"].split(",")
        self.filter_score_diff = params["filter_score_diff"]
        self.original_class_name = params["class_name"]
        self.class_name = "rank"
        self.class_type = 'd'
    
    def iterate(self, params, rep, n):
        ret = {}
        
        print "experiment", os.getcwd()
        print "iteration", n
        if n == 0:
            print "loading big set"
            shutil.copy(params["training_set"], "trainset.jcml")
        if n == 1:
            self._get_testset(params["test_set"], params["mode"], self.testset_ratio)
        
        if n == 2:
            if params.has_key("coupled_training_set"):
                print "coupled training set provided"
                os.link(params["coupled_training_set"], "trainset.coupled.jcml")
            else:
                print "coupling training set"
                simple_trainset = JcmlReader("trainset.jcml").get_dataset()
                CoupledDataSetDisk(simple_trainset).write("trainset.coupled.jcml", self.original_class_name, self.filter_score_diff, True)
                simple_trainset = None
        if n == 3:
            #there is space only for one tmp file
            flag = '/tmp/trainset.coupled.disk.run'
            time.sleep(random.randint(1,17))
            while os.path.exists(flag):
                time.sleep(31)
                print "other experiment running, no space in /tmp, waiting..."
            f = open(flag, 'w')
            
            print "converting to orange"
            SaxJcml2Orange("trainset.coupled.jcml", 
                 self.class_name,
                 self.active_attributes, 
                 self.meta_attributes, 
                 "/tmp/trainset.tab", 
                 compact_mode = True, 
                 discrete_attributes=self.discrete_attributes,
                 hidden_attributes=self.hidden_attributes,
                 get_nested_attributes=False,
                 #filter_attributes={"rank" : "0"},
                 class_type=self.class_type,
                 
                                         )
            shutil.move("/tmp/trainset.coupled.disk.tab", "trainset.coupled.disk.tab")
            f.close()
            os.remove(flag)
            

        if n == 4:
            orangeData = Table("trainset.coupled.disk.tab")
            mylearner = self.learner(**self.classifier_params) #imputer=self.imputer)
            self.myclassifier = OrangeClassifier(mylearner(orangeData))
            
        if n == 5:
            simple_testset = JcmlReader("testset.jcml").get_dataset()
            CoupledDataSetDisk(simple_testset).write("testset.coupled.jcml", self.original_class_name, -1, True)
        
        if n == 6:
            self.meta_attributes.append(self.class_name)
            print "orange version of test set"
            SaxJcml2Orange("testset.coupled.jcml", self.class_name, 
                                                 self.active_attributes, 
                                                 self.meta_attributes, 
                                                 "testset.tab", 
                                                 compact_mode=True, 
                                                 discrete_attributes=self.discrete_attributes,
                                                 hidden_attributes=self.hidden_attributes, 
                                                 get_nested_attributes=True
                                                 )
        if n == 7:
            print "performing classification"
            orangeData = Table("testset.tab")
            classified_set_vector = self.myclassifier.classify_orange_table(orangeData)
            self.classified_values_vector = [str(v[0]) for v in classified_set_vector]
            self.classified_probs_vector = [(v[1]["-1"], v[1]["1"]) for v in classified_set_vector]
#            print [str(v[1]["-1"]) for v in classified_set_vector]
#            print classified_set_vector
        
        if n == 8:
            print "EVALUATION"
            print "reloading coupled test set"
            self.simple_testset = CoupledDataSet(readfile = "testset.coupled.jcml")
        



            print "reconstructing test set"
            att_vector = [{"rank_predicted": v} for v in self.classified_values_vector]
            att_prob_neg = [{"prob_-1": v[0]} for v in self.classified_probs_vector]
            att_prob_pos = [{"prob_1": v[1]} for v in self.classified_probs_vector]
            print att_vector
            print "adding guessed rank"
            self.simple_testset.add_attribute_vector(att_vector, "ps")
            self.simple_testset.add_attribute_vector(att_prob_neg, "ps")
            self.simple_testset.add_attribute_vector(att_prob_pos, "ps")
            self.reconstructed_hard_testset = self.simple_testset.get_single_set_with_hard_ranks("rank_predicted")
            self.reconstructed_soft_testset = self.simple_testset.get_single_set_with_soft_ranks("prob_-1", "prob_1", "rank_soft_predicted")
            self.simple_testset = None
        if n == 9:
            original_score_vector = [float(ps.get_attribute("tgt-1_score")) for ps in self.reconstructed_hard_testset.get_parallelsentences()]
            #original_score_set = set(original_score_vector)
            original_score_sorted = sorted(original_score_vector, reverse=True)
            original_rank_vector = [{"rank_original": str(original_score_sorted.index(v)+1)} for v in original_score_vector]
            self.reconstructed_hard_testset.add_attribute_vector(original_rank_vector, "ps")
            if self.reconstructed_soft_testset:
                self.reconstructed_soft_testset.add_attribute_vector(original_rank_vector, "ps")
            
        if n == 10:
            ret = {}
            from support.evaluation.wmt12.wmt_scoring import WmtScoring
            ret["hard"] = WmtScoring(self.reconstructed_hard_testset).process("", "rank_original", "", "rank_predicted")
            if self.reconstructed_soft_testset:
                ret["soft"] = WmtScoring(self.reconstructed_soft_testset).process("", "rank_original", "", "rank_soft_predicted")
            print ret
            print "finished"
        return ret
        
    def save_state(self, params, rep, n):
        if n == 4:
            objectfile = open("classifier.pickle", 'w')
            pickle.dump(self.myclassifier.classifier, objectfile)
            objectfile.close()
        if n == 7:
            classified_vector_file = open("classified.hard.txt", 'w')
            for value in self.classified_values_vector:
                classified_vector_file.write("{0}\n".format(value))
            classified_vector_file.close()
            classified_prob_file = open("classified.soft.txt", 'w')
            for value1, value2 in self.classified_probs_vector:
                classified_prob_file.write("{0}\t{1}\n".format(value1, value2))
            classified_prob_file.close()
        if n == 8:
#            Parallelsentence2Jcml(self.simple_testset).write_to_file("testset.classified.jcml")
            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.hard.jcml")
            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.soft.jcml")
        if n == 9:
            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.org.hard.jcml")
            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.org.soft.jcml")
    
    def restore_state(self,params, rep, n):
        if n in [1, 5]:
            pass 
        if n in [6, 7]:
            objectfile = open("classifier.pickle", 'r')
            self.myclassifier = OrangeClassifier(pickle.load(objectfile))
            objectfile.close()
        if n == 8:
            classified_vector_file = open("classified.hard.txt", 'r') 
            self.classified_values_vector = classified_vector_file.readlines()
            classified_vector_file.close()
            classified_prob_file = open("classified.soft.txt", 'r') 
            self.classified_probs_vector = classified_prob_file.readlines()
            classified_prob_file.close()
        if n == 9:
#            self.simple_testset = JcmlReader("testset.classified.jcml").get_dataset
            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.hard.jcml").get_dataset()
            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.soft.jcml").get_dataset()
        if n == 10:
            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.org.hard.jcml").get_dataset()
            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.org.soft.jcml").get_dataset()        
    ##############################
                
    def _get_testset(self, test_filename, mode = "", ratio=0.7):
        if not test_filename == "":
            print "arbitrarily split given set to training and test sets 90% + 10%"
            simple_trainset = JcmlReader("trainset.jcml").get_dataset()
            
            if mode == "development":
                simple_trainset, a = simple_trainset.split(0.03)
            
            simple_trainset, simple_testset = simple_trainset.split(ratio)
            Parallelsentence2Jcml(simple_trainset).write_to_file("trainset.jcml")
            Parallelsentence2Jcml(simple_testset).write_to_file("testset.jcml")
        else:
            shutil.copy(test_filename, "testset.jcml")

if __name__ == '__main__':
    mysuite = QualityEstimationSuite();
    mysuite.start()
    