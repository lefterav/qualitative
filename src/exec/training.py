'''
Created on May 6, 2011

@author: Eleftherios Avramidis
'''
from orange import BayesLearner
from orange import SVMLearner
from orngTree import TreeLearner
from orngLR import LogRegLearner
from orange import kNNLearner
from io.input.orangereader import OrangeData
from io.input.xmlreader import XmlReader
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from featuregenerator.diff_generator import DiffGenerator
import sys
import ConfigParser

 

class Training(object):
    '''
    classdocs
    '''

    def __init__(self, config = None):
        '''
        Constructor
        '''
        self.classifiers = [BayesLearner(), SVMLearner(), TreeLearner(), LogRegLearner(), kNNLearner()]
        self.attribute_sets = []
        self.training_filenames = None
        self.test_filename = None
        self.class_name = "rank"
        self.convert_pairwise = True
        self.allow_ties = False
        self.generate_diff = False
        
        if config:
            self.__readconf__(config)
            
    
    def __readconf__(self, config):
        self.training_filenames = config.get("training", "filenames").split(",")
        self.test_filename = config.get("testing", "filename")
        self.class_name = config.get("training", "class_name")
        self.meta_attribute_names = config.get("training", "meta_attributes").split(",")
        for (name, value) in config.items("attributes"):
            if name.startswith("set"):
                self.add_attribute_set(value.split(","))
             
        
        
    def __get_learner__(self, name):
        for learner in self.classifiers:
            if learner.name == name:
                return learner
        return None
        
    def set_classifiers(self, classifiers):
        self.classifiers = classifiers
        
    def set_meta_attributes(self, meta_attribute_names):
        """
        The training items may have extra identifiers/comments etc that do not
        participate in the training process, but must be retained. 
        @param meta_attributes: a list of attribute names that specifies which attributes from the data object will be retained as meta attributes
        @type meta_attributes: List(String()) 
        """
        self.meta_attribute_names = meta_attribute_names
        
    def add_attribute_set(self, attribute_names):
        """
        Specify the attributes fed to the learner 
        @param meta_attributes: a list of attribute names that will be provided to the learner for training a classifier
        @type meta_attributes: List(String()) 
        """
        self.attribute_sets.append(attribute_names)
        
    def read_xml_data(self, filenames):
        dataset = None
        
        for filename in filenames:
            print "Reading XML %s " % filename
            reader = XmlReader(filename)
            parallelsentences = reader.get_parallelsentences()
            
            if self.convert_pairwise:
                parallelsentences = RankHandler().get_pairwise_from_multiclass_set(parallelsentences, self.allow_ties)

            if self.generate_diff:                 
                parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            
            cur_dataset = DataSet(parallelsentences)
            
            if not dataset:
                dataset = cur_dataset
            else:
                dataset.append_dataset(cur_dataset)
                
        #TODO: get list of attributes directly from feature generators

        return dataset
        
    def train_classifiers_attributes(self, training_xml_filenames):
        """
        Performs training of classifiers, uses them for ranking and evaluates the results on the fly
        @param training_data:
        @param test_data:
        """
        model = {}
        training_dataset = self.read_xml_data(training_xml_filenames)
        for attribute_names in self.attribute_sets:
            model[",".join(attribute_names)] = []
            #convert data with only desired atts in orange format
            training_data = OrangeData(training_dataset, self.class_name, attribute_names, self.meta_attribute_names, False)
            
            #iterate through the desired classifiers
            for learner in self.classifiers:
                #learner = self.__get_learner__(classifier_name)
                classifier = learner(training_data.get_data())
                model[",".join(attribute_names)].append((attribute_names,classifier))
        return model
    
    def rank_evaluate_and_print(self, test_xml, model):
        output = []
        test_dataset = self.read_xml_data([test_xml])
        output.append("\t")
        for classifier in self.classifiers:
            output.append(classifier.__class__.__name__)
            output.append("\t")
        output.append("\n")
        for attribute_names_string in model:
            output.append(attribute_names_string.replace(",", "\n"))
            output.append("\t")
            prev_attribute_names = []
            for (attribute_names, classifier) in  model[attribute_names_string]:
                if attribute_names != prev_attribute_names:
                    test_data = OrangeData(test_dataset, self.class_name, attribute_names, self.meta_attribute_names, False)
                prev_attribute_names = attribute_names
                
                #classified_data = test_data.classify_with(classifier)
                #parallelsentences = classified_data.get_dataset().get_parallelsentences()
                (acc, taukendal) = test_data.get_accuracy([classifier])
                #output.append(classifier.name)
                output.append("\t")
                output.append(str(taukendal[0]))
            output.append("\n")
        print "".join(output)
            
            #if self.convert_pairwise:
            #    parallelsentences = RankHandler().get_multiclass_from_pairwise_set(parallelsentences, self.allow_ties)
                
    def train_evaluate(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_evaluate_and_print(self.test_filename, model)
    

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        #initialize the experiment with the config parameters
        config = ConfigParser.RawConfigParser()
        try:
            config.read(sys.argv[1])
            training = Training(config)
            training.train_evaluate()
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            
        
            
        
        