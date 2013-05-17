'''
Created on 07 Mar 2012
@author: lefterav
'''
import logging
import copy
from collections import OrderedDict
from Orange.regression.linear import LinearRegressionLearner 
from Orange.regression.pls import PLSRegressionLearner
from Orange.regression.lasso import LassoRegressionLearner
from Orange.regression.earth import EarthLearner
from Orange.regression.tree import TreeLearner
from Orange.classification.rules import CN2Learner,  CN2UnorderedLearner, CN2SDUnorderedLearner, CN2EVCUnorderedLearner
from Orange import feature

from Orange.classification.bayes import NaiveLearner
from Orange.classification.knn import kNNLearner
#from Orange.classification.svm import SVMLearnerEasy as SVMEasyLearner
from Orange.classification.svm import SVMLearnerEasy as SVMEasyLearner
from Orange.classification.tree import TreeLearner
from Orange.classification.tree import C45Learner
from Orange.classification.logreg import LogRegLearner
from Orange import evaluation

from io_utils.input.jcmlreader import JcmlReader
#from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.sax.saxjcml2orange import SaxJcml2Orange
from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange 
from classifier.classifier import OrangeClassifier
from Orange.data import Table
from datetime import datetime

from featuregenerator.diff_generator import DiffGenerator
from sentence.pairwisedataset import AnalyticPairwiseDataset, CompactPairwiseDataset, RawPairwiseDataset
from sentence.dataset import DataSet
from sentence.scoring import Scoring

import time


import random
import sys
import shutil
import pickle
import os

from expsuite import PyExperimentSuite



class AutorankingSuite(PyExperimentSuite):
    restore_supported = True
    
    def reset(self, params, rep):
        self.restore_supported = True
        
        classifier_name = params["classifier"] + "Learner"
        self.learner = eval(classifier_name)
        try:
            self.classifier_params = eval(params["params_%s" % params["classifier"]])
        except:
            self.classifier_params = {}
        
        self.remove_infinite = False
        if classifier_name == "SVMEasyLearner":
            self.classifier_params["verbose"] = True
            self.remove_infinite = True
        
        self.meta_attributes = params["meta_attributes"].split(",")
        self.include_references = params.setdefault("include_references", False)
        self.replacement = params.setdefault("replacement", True)
        self.filter_unassigned = params.setdefault("filter_unassigned", False)
        self.restrict_ranks = params.setdefault("restrict_ranks", [])
        
        self.delay_accuracy = params.setdefault("delay_accuracy", False)
        self.remove_infinite = params.setdefault("remove_infinite", False)
        
        if self.restrict_ranks:
            self.restrict_ranks = self.restrict_ranks.split(",")
        
        source_attributes = params["{}_source".format(params["att"])].split(",")
        target_attributes = params["{}_target".format(params["att"])].split(",")
        general_attributes = params["{}_general".format(params["att"])].split(",")
        
        params["source_attributes"] = source_attributes
        params["target_attributes"] = target_attributes
        params["general_attributes"] = general_attributes
        
        self.active_attributes = []
        if general_attributes != [""]:
            self.active_attributes.extend(general_attributes) #TODOL check whether ps prefix is needed
        if source_attributes != [""]:
            self.active_attributes.extend(["src_{}".format(att) for att in source_attributes])
        if target_attributes != [""]:
            self.active_attributes.extend(["tgt-1_{}".format(att) for att in target_attributes])
            self.active_attributes.extend(["tgt-2_{}".format(att) for att in target_attributes])
        
        if self.active_attributes == [""]:
            self.active_attributes = []
        self.discretization = False
        if params.has_key("discretization"):
            self.discretization = params["discretization"]

        self.hidden_attributes = params["hidden_attributes"].split(",")
        self.discrete_attributes = params["discrete_attributes"].split(",")
 
        self.class_name = params["class_name"]
        self.class_type = params["class_type"]
        
        self.testset = params["test_set"].format(**params)
        self.ties = params["ties"]
        
        objectfile = open(params["trained_classifier"], 'r')
        self.classifier = OrangeClassifier(pickle.load(objectfile))
        objectfile.close()
    
    def iterate(self, params, rep, n):
        ret = {}
        
        if n == 10:
            print "fetch test set"
            shutil.copy(self.testset, "testset.jcml")
            self.testset = JcmlReader("testset.jcml").get_dataset() 
            
        if n == 30:
            print "pairwise testset"
            self.testset = AnalyticPairwiseDataset(self.testset, replacement = self.replacement)
            
        
        if n == 50:
            print "add difference feature : testset"
            self.pairwise_test_filename = "diff_testset.jcml"
            
            parallelsentences = self.testset.get_parallelsentences()
            parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            Parallelsentence2Jcml(parallelsentences).write_to_file(self.pairwise_test_filename)  
            
        
        if n == 70:
            print "produce orange testset"
            
            input_file = "diff_testset.jcml"
            self.testset_orange_filename = "testset.tab"
            
            if os.path.isdir("/local"):
                dir = "/local"
            else:
                dir = "."
            
            CElementTreeJcml2Orange(input_file, 
                 self.class_name,
                 self.active_attributes, 
                 self.meta_attributes, 
                 self.testset_orange_filename, 
                 compact_mode = True, 
                 discrete_attributes=self.discrete_attributes,
                 hidden_attributes=self.hidden_attributes,
                 get_nested_attributes=True,
                 dir=dir,
                 remove_infinite=self.remove_infinite
                 #filter_attributes={"rank" : "0"},
#                 class_type=class_type
                ).convert()
            
        if n == 90:
            print "test_classifier"
            
            input_file = self.testset_orange_filename
#            output_file = "classified.tab"
            
            print "performing classification"
            orangedata = Table(input_file)
            
            
           
                    
            classified_set_vector = self.classifier.classify_orange_table(orangedata)
            self.classified_values_vector = [str(v[0]) for v in classified_set_vector]
            self.classified_probs_vector = [(v[1]["-1"], v[1]["1"]) for v in classified_set_vector]
            
        
        if n == 100:
            print "Exporting results"

            self.reconstructed_soft_testset = self.simple_testset.get_single_set_with_soft_ranks("prob_-1", "prob_1", "rank_soft_predicted", "rank_soft")
            self.simple_testset = None
            
       
        return ret
    
    

    
    
    def save_state(self, params, rep, n):

        if n == 30:
            Parallelsentence2Jcml(self.testset).write_to_file("pairwise_testset.jcml")   
        if n == 50:
            Parallelsentence2Jcml(self.testset).write_to_file(self.pairwise_test_filename) 
        

        if n == 90:
            classified_vector_file = open("classified.hard.txt", 'w')
            for value in self.classified_values_vector:
                classified_vector_file.write("{0}\n".format(value))
                
            classified_vector_file.close()
            classified_prob_file = open("classified.soft.txt", 'w')
            for value1, value2 in self.classified_probs_vector:
                classified_prob_file.write("{}\t{}\n".format(value1, value2))
            classified_prob_file.close()
        if n == 100:
#            Parallelsentence2Jcml(self.simple_testset).write_to_file("testset.classified.jcml")
            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.soft.jcml")
#        if n == 110:
#            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.org.hard.jcml")
#            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.org.soft.jcml")
    
    def restore_state(self,params, rep, n):
        self.class_name = "rank" #TODO: hardcoded

        
        if n > 10 and n <=30 :
            self.testset = JcmlReader("testset.jcml").get_dataset()
        
            
        if n > 30 and n <=50:
            self.testset = JcmlReader("pairwise_testset.jcml").get_dataset()
        
        if n > 50:
            self.pairwise_test_filename = "diff_testset.jcml"
        
        if n > 70:
            self.testset_orange_filename = "testset.tab"
        
        if n > 90:
            
            classified_prob_file = open("classified.soft.txt", 'r') 
            self.classified_probs_vector = [tuple(line.split('\t')) for line in classified_prob_file]
            classified_prob_file.close()
        if n > 100:
#            self.simple_testset = JcmlReader("testset.classified.jcml").get_dataset
            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.soft.jcml").get_dataset()
#        if n == 10:
#            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.org.hard.jcml").get_dataset()
#            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.org.soft.jcml").get_dataset()        
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


def get_scoring(testset, class_name, xid, featurename):
    scoringset = Scoring(testset)
    ret = {}
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid)))
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid), suffix="-ntp", exclude_ties=False))
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid), suffix="-nt", penalize_predicted_ties=False))
#    ret["mrr"] = scoringset.mrr(featurename, class_name)
    ret["kendalltau_b-%s"%xid], ret["kendalltau_b-%s-pi"%xid]  = scoringset.get_kendall_tau_b(featurename, class_name)
    ret["b1-acc-1-%s"%xid], ret["b1-acc-%s-any"%xid] = scoringset.selectbest_accuracy(featurename, class_name)
    ret["fr-%s"%xid] = scoringset.avg_first_ranked(featurename, class_name)    
    ret["pr-%s"%xid] = scoringset.avg_predicted_ranked(featurename, class_name)
    
    sb_percentages = scoringset.best_predicted_vs_human(featurename, class_name)  
    for rank, percentage in sb_percentages.iteritems():
        ret["sb-{}-{}".format(rank,xid)] = str(percentage)
    return ret

def score(testset, class_name, xid, featurename):
    scoringset = Scoring(testset)
    return scoringset.get_metrics_scores(featurename, class_name, prefix=xid)

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
         
    def flush(self):
        pass



if __name__ == '__main__':
    FORMAT = "%(asctime)-15s [%(process)d:%(thread)d] %(message)s "
    now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
#    logging.basicConfig(filename='autoranking-{}.log'.format(now),level=logging.DEBUG, format=FORMAT)
#    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.INFO)
#    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
    mysuite = AutorankingSuite();
    mysuite.start()
    