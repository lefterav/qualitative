'''
Created on May 6, 2011

@author: Eleftherios Avramidis
'''
from orange import BayesLearner
from orange import SVMClassifier
from orange import SVMLearner
from orngSVM import SVMLearnerEasy
from orngTree import TreeLearner
from orngLR import LogRegLearner
from orange import kNNLearner
from io.input.orangereader import OrangeData
from io.input.xmlreader import XmlReader
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from sentence.scoring import Scoring
from featuregenerator.diff_generator import DiffGenerator
import sys
import ConfigParser

 

class AutoRankingExperiment(object):
    '''
    classdocs
    '''
    config = ConfigParser.RawConfigParser()

    def __init__(self, config = None, class_name = "rank"):
        '''
        Constructor
        '''
        self.classifiers = [SVMLearnerEasy, BayesLearner] #, , SVMClassifier, TreeLearner, LogRegLearner, kNNLearner]
        self.attribute_sets = []
        self.training_filenames = None
        self.test_filename = None
        self.class_name = class_name
        self.convert_pairwise = True
        #self.allow_ties = False
        self.generate_diff = False
        
        if config:
            self.__readconf__(config)
            
    
    def __readconf__(self, config):
        self.training_filenames = config.get("training", "filenames").split(",")
        self.test_filename = config.get("testing", "filename")
        try:
            self.output_filename = config.get("testing", "output_filename_base")
        except:
            self.output_filename = ""
        self.class_name = config.get("training", "class_name")
        try:
            self.orangefile = config.get("training", "orange_files_dir")
        except:
            self.orangefile = "."
        self.meta_attribute_names = config.get("training", "meta_attributes").split(",")
        self.desired_classifiers = config.get("training", "classifiers").split(",")
        try:
            self.allow_ties = config.getboolean("training", "allow_ties")
        except:
            self.allow_ties = False
        try:
            self.exponential = config.getboolean("training", "exponential")
        except:
            self.exponential = True
        try:
            self.merge_overlapping = config.getboolean("training", "merge_overlapping")
        except:
            self.merge_overlapping = True
        if "pairwise" in config.items("training") :  #TODO: this does not work, don't set false
            self.convert_pairwise = config.getboolean("training", "pairwise")
        for (name, value) in config.items("attributes"):
            if name.startswith("set"):
                self.add_attribute_set(value.split(","))
    
    def execute(self):
        trainingset = self.__get_trainingset__()
        trained_classifiers = self.__train_classifiers__(trainingset)
        
    
        testset = self.__get_testset__()
        finish_experiment = self.__finish_experiment__(trained_classifiers, testset)
        
    
    def __get_trainingset__(self):
        filenames = self.training_filenames.split(",")
        return self.__get_dataset__(filenames)
    
    
    def __get_dataset__(self, filenames):
        allparallelsentences = []
        
        for filename in filenames:
            print "Reading XML %s " % filename
            parallelsentences = XmlReader(filename).get_parallelsentences()
            
            if self.convert_pairwise:
                parallelsentences = RankHandler().get_pairwise_from_multiclass_set(parallelsentences, allow_ties, self.exponential)

            if self.generate_diff:                 
                parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            
            allparallelsentences.extend(parallelsentences)
            
        if self.merge_overlapping:
            allparallelsentences = RankHandler().merge_overlapping_pairwise_set(allparallelsentences)
           
        #TODO: get list of attributes directly from feature generators
        return DataSet(allparallelsentences)  
  

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        #initialize the experiment with the config parameters
        config = ConfigParser.RawConfigParser()
        try:
            print sys.argv[1]
            config.read(sys.argv[1])
            exp = AutoRankingExperiment(config)
            
            
            try:
                mode = config.get("testing", "mode")
            except:
                mode = "evaluate"
                
            if mode == "evaluate":
                exp.train_evaluate()
            elif mode == "decode":
                exp.train_decode()
            elif mode == "decodebest":
                print "Decoding only for best"
                exp.train_decodebest()
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            
        
            
        
        
