'''
Created on 07 Mar 2012
@author: lefterav
'''
import logging
import copy

from Orange.data import Domain

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
from classifier.svmeasy import SVMEasyLearner
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

from featuregenerator.diff_generator import DiffGenerator
from sentence.pairwisedataset import AnalyticPairwiseDataset, CompactPairwiseDataset
from sentence.dataset import DataSet
from sentence.scoring import Scoring

import time

import random
import sys
import shutil
import pickle
import os

from expsuite import PyExperimentSuite
from time import gmtime, strftime


class AutorankingSuite(PyExperimentSuite):
    restore_supported = True
    
    def reset(self, params, rep):
        self.restore_supported = True
        
        #define one classifier
        classifier_name = params["classifier"] + "Learner"
        self.learner = eval(classifier_name)
        try:
            self.classifier_params = eval(params["params_%s" % params["classifier"]])
        except:
            self.classifier_params = {}
        
        self.meta_attributes = params["meta_attributes"].split(",")
        
 
        self.class_name = params["class_name"]
        self.class_type = params["class_type"]
        
        self.ties = params["ties"]
        
        self.trainset_orange_filename = params["training_tab"].format(**params)
        self.pairwise_test_filename = params["test_tab"].format(**params)
        
        self.critical_score = params["critical_score"]

        self.attributes = set(params[params["att"]].split(","))
    
    
    def iterate(self, params, rep, n):
        ret = {}
        
        if n == 80:
            logging.info("===== TRAINING CLASSIFIER =====")
            input_file = self.trainset_orange_filename
            
            trainset = Table(input_file)
            new_attributes = []
            new_attributes.extend(self.attributes)
            new_attributes.append(self.class_name)
            newdomain = Domain(new_attributes, trainset.domain)
            newtrainset = Table(newdomain, trainset)
            logging.debug("Original domain reduced from %d features to %d features including class. \nFinal features = %s ", len(trainset.domain), len(newtrainset.domain), newtrainset.domain)
            
            
            cltimestart = time.time()
            mylearner = self.learner(**self.classifier_params)
            trained_classifier = mylearner(newtrainset)
            self.classifier = OrangeClassifier(trained_classifier)
            self.classifier.print_content()
            cltimeend = time.time()
            ret["training_time"] = cltimeend - cltimestart
        
        if n == 85:
            logging.info("evaluate classifier with cross-fold validation")
            orangeData = Table(self.trainset_orange_filename)
            learner = self.learner(**self.classifier_params)
            cv = evaluation.testing.cross_validation([learner], orangeData, 10)
            ret["CA"] = evaluation.scoring.CA(cv)[0]
            ret["AUC"] = evaluation.scoring.AUC(cv)[0]

        if self.critical_score not in ["CA", "AUC"]:
            if n == 90:
                logging.info("==== TESTING CLASSIFIER ====")
                
                orangedata = Table(self.testset_orange_filename)                         
                classified_set_vector = self.classifier.classify_orange_table(orangedata)
                
                self.classified_values_vector = [str(v[0]) for v in classified_set_vector]
                self.classified_probs_vector = [(v[1]["-1"], v[1]["1"]) for v in classified_set_vector]
                
            if n == 100:
                logging.info("==== EVALUATION TESTSET ====")
                logging.info("== reloading coupled test set ==")
                self.simple_testset = JcmlReader(self.pairwise_test_filename).get_dataset()
                
                logging.info("reconstructing test set")
                att_vector = [{"rank_predicted": v} for v in self.classified_values_vector]
                att_prob_neg = [{"prob_-1": v[0]} for v in self.classified_probs_vector]
                att_prob_pos = [{"prob_1": v[1]} for v in self.classified_probs_vector]
                
                logging.info("adding guessed rank")
                self.simple_testset.add_attribute_vector(att_vector, "ps")
                self.simple_testset.add_attribute_vector(att_prob_neg, "ps")
                self.simple_testset.add_attribute_vector(att_prob_pos, "ps")
                
                self.simple_testset = AnalyticPairwiseDataset(self.simple_testset) #this 
                self.simple_testset = CompactPairwiseDataset(self.simple_testset) #and this should have no effect
                
                self.reconstructed_hard_testset = self.simple_testset.get_single_set_with_hard_ranks("rank_predicted", "rank_hard")
                self.reconstructed_soft_testset = self.simple_testset.get_single_set_with_soft_ranks("prob_-1", "prob_1", "rank_soft_predicted", "rank_soft")
                self.simple_testset = None
                
            
            if n == 120:
                logging.info("== Scoring correlation ==")
                scoringset = Scoring(self.reconstructed_hard_testset)
                ret["kendalltau-hard"], ret["kendalltau-hard-pi"]  = scoringset.get_kendall_tau("rank_hard", self.class_name)
                ret["kendalltau_b-hard"], ret["kendalltau_b-hard-pi"]  = scoringset.get_kendall_tau_b("rank_hard", self.class_name)
                ret["b1-acc-hard-1"], ret["b1-acc-hard-any"] = scoringset.selectbest_accuracy("rank_hard", self.class_name)            
                
                scoringset = Scoring(self.reconstructed_soft_testset)
                ret["kendalltau-soft"], ret["kendalltau-soft-pi"] = scoringset.get_kendall_tau("rank_soft", self.class_name)
                ret["kendalltau_b-soft"], ret["kendalltau_b-soft-pi"] = scoringset.get_kendall_tau_b("rank_soft", self.class_name)
                ret["b1-acc-soft-1"], ret["b1-acc-soft-any"] = scoringset.selectbest_accuracy("rank_soft", self.class_name)        
                
            
        return ret
#        
#    def save_state(self, params, rep, n):
#        if n == 0:
#            Parallelsentence2Jcml(self.trainset).write_to_file("trainset.jcml") 
#        if n == 20:
#            Parallelsentence2Jcml(self.trainset).write_to_file("pairwise_trainset.jcml")
#        if n == 30:
#            Parallelsentence2Jcml(self.testset).write_to_file("pairwise_testset.jcml")   
#        if n == 40:
#            pass
#        if n == 50:
#            Parallelsentence2Jcml(self.testset).write_to_file(self.pairwise_test_filename) 
#        
#        if n == 80:
#            objectfile = open(self.output_file, 'w')
#            pickle.dump(self.classifier.classifier, objectfile)
#            objectfile.close()
#        if n == 90:
#            classified_vector_file = open("classified.hard.txt", 'w')
#            for value in self.classified_values_vector:
#                classified_vector_file.write("{0}\n".format(value))
#                
#            classified_vector_file.close()
#            classified_prob_file = open("classified.soft.txt", 'w')
#            for value1, value2 in self.classified_probs_vector:
#                classified_prob_file.write("{0}\t{1}\n".format(value1, value2))
#            classified_prob_file.close()
#        if n == 100:
##            Parallelsentence2Jcml(self.simple_testset).write_to_file("testset.classified.jcml")
#            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.hard.jcml")
#            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.soft.jcml")
##        if n == 110:
##            Parallelsentence2Jcml(self.reconstructed_hard_testset).write_to_file("testset.reconstructed.org.hard.jcml")
##            Parallelsentence2Jcml(self.reconstructed_soft_testset).write_to_file("testset.reconstructed.org.soft.jcml")
#    
#    def restore_state(self,params, rep, n):
#        
#        if n > 0 and n <=20 :
#            self.trainset = JcmlReader("trainset.jcml").get_dataset()
#        
#        if n > 10 and n <=30 :
#            self.testset = JcmlReader("testset.jcml").get_dataset()
#        
#        if n > 20 and n <=40:
#            self.trainset =  JcmlReader("pairwise_trainset.jcml").get_dataset()
#            
#        if n > 30 and n <=50:
#            self.testset = JcmlReader("pairwise_testset.jcml").get_dataset()
#        
#        if n > 50:
#            self.pairwise_test_filename = "diff_testset.jcml"
#            self.trainset_orange_filename = "trainset.tab"
#        
#        if n > 70:
#            self.testset_orange_filename = "testset.tab"
#        
#        if n > 80 and n <= 90:
#            objectfile = open("classifier.clsf", 'r')
#            self.classifier = OrangeClassifier(pickle.load(objectfile))
#            objectfile.close()
#        if n > 90:
#            classified_vector_file = open("classified.hard.txt", 'r') 
#            self.classified_values_vector = classified_vector_file.readlines()
#            classified_vector_file.close()
#            classified_prob_file = open("classified.soft.txt", 'r') 
#            self.classified_probs_vector = [tuple(line.split('\t')) for line in classified_prob_file]
#            classified_prob_file.close()
#        if n > 100:
##            self.simple_testset = JcmlReader("testset.classified.jcml").get_dataset
#            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.hard.jcml").get_dataset()
#            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.soft.jcml").get_dataset()
##        if n == 10:
##            self.reconstructed_hard_testset = JcmlReader("testset.reconstructed.org.hard.jcml").get_dataset()
##            self.reconstructed_soft_testset = JcmlReader("testset.reconstructed.org.soft.jcml").get_dataset()        
#    ##############################
                
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


import argparse, ConfigParser
from operator import itemgetter
import shutil

def load_data():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', nargs=1, help="configuration file")
    parser.add_argument('-e', nargs=1, help="experiment name")
    parser.add_argument('-n', nargs='?', help="cores num")
    parser.add_argument('-d', nargs='?', help="delete previous")
    args = parser.parse_args()
    configfile = args.c[0]
    print configfile
    experiment = args.e[0]
    
    cparser = ConfigParser.ConfigParser()
    cparser.read(configfile)
    trainset_orange_filename = eval(cparser.get(experiment, "training_tab"))
    critical_score = eval(cparser.get(experiment, "critical_score"))
    path = cparser.get("DEFAULT", "path")
    exppath = os.path.join(path, experiment)
    shutil.rmtree(exppath, True)
    os.mkdir(exppath)
    
    orangedata = Table(trainset_orange_filename)
    return orangedata, cparser, experiment, critical_score, path


def get_new_config(initial_config, path, featuresets, experiment, repetition):
    i = 0
    attsets = []
    for featureset in featuresets:
        featureset = [feature for feature in featureset]
        featureset = '"{}"'.format(",".join(featureset))
        i+=1
        attset_id = "attset_{}".format(i)
        initial_config.set(experiment, attset_id, featureset)
        initial_config.set(experiment, "repetition", "[{}]".format(repetition))
        attsets.append('"{}"'.format(attset_id))
    attsets = "[{}]".format(",".join(attsets))
    initial_config.set(experiment, "att", attsets)
    filename = os.path.join(path, experiment, "experiment_{}.cfg".format(repetition))
    f = open(filename, "w")
    initial_config.write(f)
    f.close()
    return filename

def filter_features(features):

    allowed_features = []
    filters = ["_matches", "Satz_zu_lang", "_chars"]
    for feature in features:
        filtering = False
        for filterout in filters:
            if filterout in feature.name:
                filtering = True
        if not filtering:
            allowed_features.append(feature)
    return allowed_features

def get_new_commandline_args(newconfig_filename):
    new_argv = sys.argv
    i = 0
    for argv in sys.argv:
        
        if argv in ["-c", "--config"]:
            new_argv[i+1] = newconfig_filename
            break
        i+=1
    
    sys.argv = new_argv


def get_scores(mysuite, path, exp, critical_score, **kwargs):
    exps = mysuite.get_exps(path=path)
    feature_scores = []
    
    max_len = 0
    for exp in exps:
        rep = 0
        value = mysuite.get_value(exp, rep, critical_score)
        
        if value:
            params = mysuite.get_params(exp)
            attset_id = params["att"]
            featureset = params[attset_id].split(",")
            if len(featureset)> max_len:
                max_len = len(featureset)
            feature_scores.append((featureset, float(value)))
    
    feature_scores = [(featureset, value) for featureset, value in feature_scores if len(featureset) == max_len]
    feature_scores = sorted(feature_scores, key=itemgetter(1), reverse=True)
    prune = kwargs.setdefault("prune", False)
    if prune:
        feature_scores = feature_scores[0:prune]
    return feature_scores


def get_new_featuresets(featureset_scores, previous_value):
    best_featureset, best_value = featureset_scores[0]
    converged = False
    new_featuresets = []
    if best_value < previous_value:
        converged = True
        logging.info("None of the alternatives improved score, stopping")
        return converged, new_featuresets
    for featureset, value in featureset_scores[1:]:
        if value >= previous_value:
            lastfeature = featureset[-1]
            new_featureset = copy.copy(best_featureset)
            new_featureset.append(lastfeature)
            if not set(new_featureset) == set(best_featureset) and new_featureset not in new_featuresets:
                new_featuresets.append(new_featureset)
        logging.debug("New featureset has a length of %d", len(new_featureset))
    if new_featuresets == []:
        converged = True
        logging.info("There are no further featureset expansions possible. The current best featureset is %s", best_featureset)
    return converged, new_featuresets


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
 
 
if __name__ == '__main__':
    converged = False
    
    repetition = 0
    orangedata, config, experiment, critical_score, path = load_data()
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(filename=os.path.join(path, experiment, 'search.log'),level=logging.DEBUG,format=FORMAT)
    
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.INFO)
    sys.stderr = sl
    
    logging.info("Working in path %s", path)
    logging.info("Original features are %d", len(orangedata.domain.features))
    
    allowed_features = filter_features(orangedata.domain.features)
    featuresets = [[feature.name] for feature in allowed_features][:10]
    previous_value = 0
    previous_len = 0
    
    while not converged:
        repetition += 1
        
        #creat a new configfile and pass it by overriding commandline params
        newconfig_filename = get_new_config(config, path, featuresets, experiment, repetition)
        logging.debug("Iteration filename %s", newconfig_filename)
        get_new_commandline_args(newconfig_filename)
        
        #run the experiment
        mysuite = AutorankingSuite()
        mysuite.start()
        
        featureset_scores = get_scores(mysuite, path, experiment, critical_score)
        logging.debug("Featureset scores: \n%s\n", featureset_scores)
        logging.info("Best score for iteration %d = %s", repetition,  featureset_scores[0][1])
        logging.info("Featureset %s", featureset_scores[0][0])
        #the featureset to augment
        
        converged, featuresets = get_new_featuresets(featureset_scores, previous_value)
        
        
    

        
    
    
#    while not converged:
#        modify_params()
#        mysuite = AutorankingSuite()
#        mysuite.start()
#        check_results()
#    