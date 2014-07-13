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
from io_utils.input.orangereader import OrangeData
from io_utils.input.xmlreader import XmlReader
from io_utils.output.xmlwriter import XmlWriter  
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from sentence.scoring import Scoring
from featuregenerator.diff_generator import DiffGenerator
import sys
import ConfigParser

import classifier
import pkgutil
import orange
import cPickle as pickle
import os
import shutil
 

class AutoRankingExperiment(object):
    '''
    classdocs
    '''
    config = ConfigParser.RawConfigParser()

    def __init__(self, configfile, step = None):
        '''
        Constructor
        '''
        self.step = step
        self._readconf(configfile)
        self.ready_classifier = None
        self.ready_testset_orng = None
    
    def _readconf(self, configfile):
        config = ConfigParser.RawConfigParser()
        config.read(["default.cfg", configfile])
        path = config.get("general", "path")
        
        if self.step:
            self.dir = self._resume_dir(path, configfile, self.step)
        else:
            self.dir = self._prepare_dir(path, configfile)
        

        #training
        classifier_name = config.get("training", "classifier")
        self.classifier = self._get_classifier_from_name(classifier_name)
        
        self.continuize = config.getboolean("training", "continuize")
        self.classifier_params = {"multinomialTreatment" : self._get_continuizer_constant(config.get("training", "multinomialTreatment")),
                                 "continuousTreatment" : self._get_continuizer_constant(config.get("training", "continuousTreatment")),
                                 "classTreatment" : self._get_continuizer_constant(config.get("training", "classTreatment"))}
                
        self.allow_ties = config.getboolean("training", "allow_ties")
        self.exponential = config.getboolean("training", "exponential")
        self.merge_overlapping = config.getboolean("training", "merge_overlapping")
        self.generate_diff = config.getboolean("training", "generate_diff")
        self.convert_pairwise = config.getboolean("training", "convert_pairwise")
        self.orange_minimal = config.getboolean("training", "orange_minimal")
        
        self.training_filenames = config.get("training", "filenames").split(",")
        self.class_name = config.get("training", "class_name")
        
        try:
            self.meta_attribute_names = config.get("training", "meta_attributes")
            self.attribute_names = config.get("training", "attributes")
        except:
            self._print_attributes()
            sys.exit()
        #testing
        self.test_filename = config.get("testing", "filename")
        self.test_mode = config.get("testing", "mode")
        
    def _prepare_dir(self, path, configfile, step = None):
        try:
            existing_files = os.listdir(path)
        except:
            os.makedirs(path)
            existing_files = []
        
        filenames = []
        for filename in existing_files:
            try:
                filenames.append(int(filename))
            except:
                pass
        if filenames:
            highestnum = max(filenames)
            newnum = highestnum + 1
        else:
            newnum = 1
        path = os.path.join(path, str(newnum))
        os.mkdir(path)
        os.chdir(path)
        shutil.copy(configfile, path)
        return path
        
    def _resume_dir(self, path, configfile, step):
        path = os.path.join(path, str(step))
        os.chdir(path)
        existing_files = os.listdir(path)
        if "classifier.pickle" in existing_files:
            mypickle = open("classifier.pickle", "r")
            self.ready_classifier = pickle.load(mypickle)
            mypickle.close()
        if "testdata.tab" in existing_files:
            self.ready_testset_orng = orange.ExampleTable("testdata.tab")
        

    def _get_classifier_from_name(self, name):
        package = classifier
        prefix = package.__name__ + '.'
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            module = __import__(modname, fromlist="dummy")
            try:
                return getattr(module, name)
            except:
                pass
        return getattr(orange, name)
    
    def _get_continuizer_constant(self, name):
        return getattr(orange.DomainContinuizer, name)
  
  
    def _print_attributes(self):
        trainingset_jcml = self._get_trainingset()
        print "Available attributes in dataset:"
        print ",".join(trainingset_jcml.get_all_attribute_names())
            
    def execute(self):
        if not self.ready_testset_orng:
            testset_jcml = self._get_testset()
            orangefilename = "%s/testdata.tab" % self.dir
            testset_orng = OrangeData(testset_jcml, self.class_name, self.attribute_names, self.meta_attribute_names, orangefilename, self.orange_minimal)
        else:
            testset_orng = self.ready_testset_orng
        
        if not self.ready_classifier:
            trainingset_jcml = self._get_trainingset()
            orangefilename = "%s/trainingdata.tab" % self.dir 
            trainingset_orng = OrangeData(trainingset_jcml, self.class_name, self.attribute_names, self.meta_attribute_names, orangefilename, self.orange_minimal)
                        
            myclassifier = self.classifier()
            try:
                trained_classifier = myclassifier.learnClassifier(trainingset_orng.get_data(), self.classifier_params)
            except AttributeError:
                trained_classifier = myclassifier(trainingset_orng.get_data())
            objectfile = open("%s/classifier.pickle" % self.dir, 'w')
            pickle.dump(trained_classifier, objectfile)
            objectfile.close()
        
        else:    
            trained_classifier = self.ready_classifier
        
        if self.test_mode == "evaluate":
            classified_orng, accuracy, taukendall = testset_orng.classify_accuracy(trained_classifier)
        else:
            classified_orng = testset_orng.classify_with(trained_classifier)
        parallelsentences_multiclass = RankHandler(self.class_name).get_multiclass_from_pairwise_set(classified_orng.get_dataset(), True)
        XmlWriter(parallelsentences_multiclass).write_to_file("%s/classified.jcml" % self.dir)
        
        if self.test_mode == "evaluate":
            self._get_statistics(parallelsentences_multiclass, accuracy, taukendall)
        
        #finish_experiment = self._finish_experiment(trained_classifier, testset)
    def _get_statistics(self, parallelsentences, accuracy, taukendall):
        output = []
        output.append(("pairwise accuracy", str(accuracy)))
        output.append(("pairwise tau", str(taukendall)))
        
        scoringset = Scoring(parallelsentences)
#        (rho, p) = scoringset.get_spearman_correlation(self.class_name, "orig_rank")
#        output.append(("Spearman rho" , str(rho)))
#        output.append(("Spearman p" , str(p)))
        
        kendalltau = scoringset.get_kendall_tau(self.class_name, "orig_rank")
        output.append(("actual tau", str(kendalltau)))
        
        accuracy, precision = scoringset.selectbest_accuracy(self.class_name, "orig_rank") 
        
        output.append(("select best acc", str(accuracy)))
        output.append(("select best prec", str(precision)))
        
        resultsfile = open("results.tab", 'w')
        resultsfile.writelines(["%s\t%s" % (description, value) for (description, value) in output])
        resultsfile.close()
    
    def _get_trainingset(self):
        filenames = self.training_filenames
        return self._get_dataset(filenames, self.allow_ties)
    
    def _get_testset(self):
        filename = self.test_filename
        return self._get_dataset([filename], True)
    
    def _get_dataset(self, filenames, allow_ties):
        allparallelsentences = []
        
        for filename in filenames:
            print "Reading XML %s " % filename
            parallelsentences = XmlReader(filename).get_parallelsentences()
            
            if self.convert_pairwise:
                parallelsentences = RankHandler(self.class_name).get_pairwise_from_multiclass_set(parallelsentences, allow_ties, self.exponential)

            if self.generate_diff:                 
                parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            
            allparallelsentences.extend(parallelsentences)
            
        if self.merge_overlapping:
            allparallelsentences = RankHandler(self.class_name).merge_overlapping_pairwise_set(allparallelsentences)
           
        #TODO: get list of attributes directly from feature generators
        return DataSet(allparallelsentences)  
  
    
        

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        
    else:
        
        try:
            print sys.argv[1]
            
            try:
                if sys.argv[2] == "-continue":
                    continue_step = int(sys.argv[3])
                    exp = AutoRankingExperiment(sys.argv[1], continue_step)
            except:
                exp = AutoRankingExperiment(sys.argv[1])
            
            exp.execute()
            
            
            
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            
        
            
        
        
