'''
Created on 07 Mar 2012
@author: Eleftherios Avramidis
'''
import logging
import copy
from collections import OrderedDict
from Orange.regression.linear import LinearRegressionLearner 
from Orange.regression.pls import PLSRegressionLearner
from Orange.regression.lasso import LassoRegressionLearner
#from Orange.regression.earth import EarthLearner
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
from Orange.classification.logreg import LibLinearLogRegLearner
from Orange import evaluation

from dataprocessor.input.jcmlreader import JcmlReader
#from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from dataprocessor.jcml.writer import Parallelsentence2Jcml
from dataprocessor.sax.saxjcml2orange import SaxJcml2Orange
from dataprocessor.ce.cejcml2orange import CElementTreeJcml2Orange 
from ml.var.classifier import OrangeClassifier
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
        
        classifier_name = params["learner"] + "Learner"
        self.learner = eval(classifier_name)
        try:
            self.classifier_params = eval(params["params_{}".format(params["learner"]).lower()])
        except:
            self.classifier_params = {}
        
        sys.stderr.write("Accepted learner parameters: {}\n".format(self.classifier_params))
        self.remove_infinite = False
        self.delay_accuracy =  False
        if classifier_name == "SVMEasyLearner":
            self.classifier_params["verbose"] = True
            self.remove_infinite = True
            self.delay_accuracy = True
        
        self.meta_attributes = params["meta_attributes"].split(",")
        self.include_references = params.setdefault("include_references", False)
        self.replacement = params.setdefault("replacement", True)
        self.filter_unassigned = params.setdefault("filter_unassigned", False)
        self.restrict_ranks = params.setdefault("restrict_ranks", [])
        
        self.delay_accuracy = params.setdefault("delay_accuracy", self.delay_accuracy)
        self.remove_infinite = params.setdefault("remove_infinite", False)
        self.nullimputation = params.setdefault("nullimputation", False)
        
        self.invert_ranks = params.setdefault("invert_ranks", False)
        self.evaluation_invert_ranks = params.setdefault("evaluation_invert_ranks", False)
        
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
        
        self.training_sets = params["training_sets"].format(**params).split(',')
        self.testset = params["test_set"].format(**params)
        self.ties = params["ties"]
    
    
    def iterate(self, params, rep, n):
        ret = {}
        
#        print "app", os.getcwd()
#        print "iteration", n
        
#        if n == 0:
#            import annotate_updated as annotate
#            from ruffus import pipeline_run
#            pipeline_run([annotate.analyze_external_features]) 
        
        if n == 0:
            print "fetch training set"
            parallelsentences = []
            for training_set in self.training_sets:
                parallelsentences.extend(JcmlReader(training_set).get_parallelsentences())
            
            self.trainset = DataSet(parallelsentences)  
        
        #TODO: alter training filters?
        
        if n == 10:
            print "fetch test set"
            shutil.copy(self.testset, "testset.jcml")
            self.testset = JcmlReader("testset.jcml").get_dataset() 
            
        if n == 20:
            print "pairwise training set"
                
            self.trainset = AnalyticPairwiseDataset(
                                                    self.trainset, include_references = self.include_references, 
                                                    replacement = self.replacement, 
                                                    filter_unassigned = self.filter_unassigned,
                                                    restrict_ranks = self.restrict_ranks,
                                                    invert_ranks = self.invert_ranks
                                                    )
            
            if not self.ties:  
                self.trainset.remove_ties()
            
            #SAVE
            Parallelsentence2Jcml(self.trainset).write_to_file("pairwise_trainset.jcml")    
            
        if n == 30:
            print "pairwise testset"
            self.testset = AnalyticPairwiseDataset(self.testset, replacement = self.replacement, invert_ranks = self.invert_ranks)
            
 
        
        if n == 40:
            #print "add difference features : trainset"
            #parallelsentences = self.trainset.get_parallelsentences()
            #parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            #Parallelsentence2Jcml(parallelsentences).write_to_file("diff_trainset.jcml")  
            pass

        
        
        if n == 50:
            #print "add difference feature : testset"
            self.pairwise_test_filename = "pairwise_testset.jcml"
            
            #parallelsentences = self.testset.get_parallelsentences()
            #parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            #Parallelsentence2Jcml(parallelsentences).write_to_file(self.pairwise_test_filename)  
            pass
            
        
        if n == 60:
            print "produce orange trainset"
            
            input_file = "pairwise_trainset.jcml"
            self.trainset_orange_filename = "trainset.tab"
            
            if os.path.isdir("/local/tmp/elav01"):
                dir = "/local/tmp/elav01"
            else:
                dir = "."
            
            
            CElementTreeJcml2Orange(input_file, 
                 self.class_name,
                 self.active_attributes, 
                 self.meta_attributes, 
                 self.trainset_orange_filename, 
                 compact_mode = True, 
                 discrete_attributes=self.discrete_attributes,
                 hidden_attributes=self.hidden_attributes,
                 get_nested_attributes=True,
                 dir=dir,
                 remove_infinite=self.remove_infinite,
                 nullimputation=self.nullimputation,
                 #filter_attributes={"rank_strings" : "0"},
#                 class_type=class_type
                ).convert()
        
        
        if n == 70:
            print "produce orange testset"
            
            input_file = "pairwise_testset.jcml"
            self.testset_orange_filename = "testset.tab"
            
            if os.path.isdir("/local/tmp/elav01"):
                dir = "/local/tmp/elav01"
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
                 remove_infinite=self.remove_infinite,
                 nullimputation=self.nullimputation,
                 #filter_attributes={"rank_strings" : "0"},
#                 class_type=class_type
                ).convert()
            
        if n == 80:
            print "train learner"
            input_file = self.trainset_orange_filename 
            self.output_file = "learner.clsf"
            
            trainset = Table(input_file)
            
            mylearner = self.learner(**self.classifier_params)
            trained_classifier = mylearner(trainset)
            self.learner = OrangeClassifier(trained_classifier)
            self.learner.print_content()
            
        
        #give the possibility to calculate classification accuracy in the end
        if (n == 85 and not self.delay_accuracy) or (n == 185 and self.delay_accuracy):
            print "evaluate learner with cross-fold validation"
            orangeData = Table(self.trainset_orange_filename)
            learner = self.learner(**self.classifier_params)
            cv = evaluation.testing.cross_validation([learner], orangeData, 10)
            ret["CA"] = evaluation.scoring.CA(cv)[0]
            ret["AUC"] = evaluation.scoring.AUC(cv)[0]
            
        if n == 90:
            print "test_classifier"
            
            input_file = self.testset_orange_filename
#            output_file = "classified.tab"
            
            print "performing classification"
            orangedata = Table(input_file)
            
            
           
                    
            classified_set_vector = self.learner.classify_orange_table(orangedata)
            self.classified_values_vector = [str(v[0]) for v in classified_set_vector]
            self.classified_probs_vector = [(v[1]["-1"], v[1]["1"]) for v in classified_set_vector]
            
            
#            print [str(v[1]["-1"]) for v in classified_set_vector]
#            print classified_set_vector
        
#        if n == 95:
#            print "accuracy over test set"
#            orangedata = Table(self.testset_orange_filename)
#            cv = evaluation.testing.default_evaluation([self.learner(**self.classifier_params)], orangedata)
#            ret["CA_test"] = evaluation.scoring.CA(cv)
#            ret["AUC_test"] = evaluation.scoring.AUC(cv)
        
        
        if n == 100:
            print "EVALUATION"
            print "reloading coupled test set"
            self.simple_testset = JcmlReader(self.pairwise_test_filename).get_dataset()
            
            print "reconstructing test set"
            att_vector = [{"rank_predicted": v} for v in self.classified_values_vector]
            att_prob_neg = [{"prob_-1": v[0]} for v in self.classified_probs_vector]
            att_prob_pos = [{"prob_1": v[1]} for v in self.classified_probs_vector]
#            print att_vector
            
            print "adding guessed rank_strings"
            self.simple_testset.add_attribute_vector(att_vector, "ps")
            self.simple_testset.add_attribute_vector(att_prob_neg, "ps")
            self.simple_testset.add_attribute_vector(att_prob_pos, "ps")
            
            
            Parallelsentence2Jcml(self.simple_testset).write_to_file("testset-pairwise-with-estranks.jcml")
            
            self.simple_testset = RawPairwiseDataset(cast=self.simple_testset) #this 
#            self.simple_testset = CompactPairwiseDataset(self.simple_testset) #and this should have no effect
            
            self.reconstructed_hard_testset = self.simple_testset.get_single_set_with_hard_ranks("rank_predicted", "rank_hard")
            self.reconstructed_soft_testset = self.simple_testset.get_single_set_with_soft_ranks("prob_-1", "prob_1", "rank_soft_predicted", "rank_soft")
            self.simple_testset = None
            
        
        if n == 120:
            print "Scoring correlation"
            print "ranks inverted ", self.evaluation_invert_ranks
            ret.update(score(self.reconstructed_hard_testset, self.class_name, "hard", "rank_hard", self.evaluation_invert_ranks))
            ret.update(score(self.reconstructed_soft_testset, self.class_name, "soft", "rank_soft", self.evaluation_invert_ranks))
            ret = OrderedDict(sorted(ret.items(), key=lambda t: t[0]))
         
            print ret   
        return ret
    
    

    
    
    def save_state(self, params, rep, n):
        if n == 0:
            Parallelsentence2Jcml(self.trainset).write_to_file("trainset.jcml") 
        if n == 20:
            Parallelsentence2Jcml(self.trainset).write_to_file("pairwise_trainset.jcml")
        if n == 30:
            Parallelsentence2Jcml(self.testset).write_to_file("pairwise_testset.jcml")   
        if n == 40:
            pass
        if n == 50:
            Parallelsentence2Jcml(self.testset).write_to_file(self.pairwise_test_filename) 
        
        if n == 80:
            objectfile = open(self.output_file, 'w')
            pickle.dump(self.learner.learner, objectfile)
            objectfile.close()
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
            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.hard.jcml")
            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.soft.jcml")
#        if n == 110:
#            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.org.hard.jcml")
#            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.org.soft.jcml")
    
    def restore_state(self,params, rep, n):
        self.class_name = "rank_strings" #TODO: hardcoded
        if n > 0 and n <=20 :
            self.trainset = JcmlReader("trainset.jcml").get_dataset()
        
        if n > 10 and n <=30 :
            self.testset = JcmlReader("testset.jcml").get_dataset()
        
        if n > 20 and n <=40:
            self.trainset =  JcmlReader("pairwise_trainset.jcml").get_dataset()
            
        if n > 30 and n <=50:
            self.testset = JcmlReader("pairwise_testset.jcml").get_dataset()
        
        if n > 50:
            self.pairwise_test_filename = "pairwise_testset.jcml"
            self.trainset_orange_filename = "trainset.tab"
        
        if n > 70:
            self.testset_orange_filename = "testset.tab"
        
        if n > 80 and n <= 90:
            objectfile = open("learner.clsf", 'r')
            self.learner = OrangeClassifier(pickle.load(objectfile))
            objectfile.close()
        if n > 90:
            
            classified_vector_file = open("classified.hard.txt", 'r') 
            self.classified_values_vector = classified_vector_file.readlines()
            classified_vector_file.close()
            classified_prob_file = open("classified.soft.txt", 'r') 
            self.classified_probs_vector = [tuple(line.split('\t')) for line in classified_prob_file]
            classified_prob_file.close()
        if n > 100:
#            self.simple_testset = JcmlReader("testset.classified.jcml").get_dataset
            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.hard.jcml").get_dataset()
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
    for rank_strings, percentage in sb_percentages.iteritems():
        ret["sb-{}-{}".format(rank_strings,xid)] = str(percentage)
    return ret

def score(testset, class_name, xid, featurename, invert_ranks=False):
    scoringset = Scoring(testset, invert_ranks=invert_ranks)
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
    
