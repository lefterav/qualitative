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
from sentence.scoring import Scoring
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
        self.classifiers = [BayesLearner, SVMLearner, TreeLearner, LogRegLearner, kNNLearner]
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
        try:
            self.output_filename = config.get("testing", "output_filename_base")
        except:
            self.output_filename = None
        self.class_name = config.get("training", "class_name")
        self.meta_attribute_names = config.get("training", "meta_attributes").split(",")
        self.desired_classifiers = config.get("training", "classifiers").split(",")
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
            parallelsentences = XmlReader(filename).get_parallelsentences()
            
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
            training_data = OrangeData(training_dataset, self.class_name, attribute_names, self.meta_attribute_names, True)
            
            #iterate through the desired classifiers
            for learner in self.classifiers:
                if not learner().__class__.__name__ in self.desired_classifiers:
                    continue
                #learner = self.__get_learner__(classifier_name)
                if isinstance(learner(), kNNLearner):
                    print "kNN!"
                    classifier = learner(training_data.get_data(), 20)
                else:
                    classifier = learner(training_data.get_data())
                model[",".join(attribute_names)].append((attribute_names, classifier))
        return model
            
    
    def rank_and_export(self, test_xml, filename_out, model):
        output = []
        test_dataset_pairwise = self.read_xml_data([test_xml])
        output.append("\t")
        for classifier in self.classifiers:
            if not classifier().__class__.__name__ in self.desired_classifiers:
                continue
            output.append(classifier().__class__.__name__)
            output.append("\t")
        output.append("\n")
        for attribute_names_string in model:
            output.append(attribute_names_string.replace(",", "\n"))
            output.append("\t")
            prev_attribute_names = []
            i = 0
            for (attribute_names, classifier) in  model[attribute_names_string]:
                i = i+1
                if attribute_names != prev_attribute_names:
                    test_data_pairwise = OrangeData(test_dataset_pairwise, self.class_name, attribute_names, self.meta_attribute_names, True)
                prev_attribute_names = attribute_names
                
                #output.append(classifier.name)
                classified_pairwise = test_data_pairwise.classify_with(classifier)
                parallelsentences = RankHandler().get_multiclass_from_pairwise_set(classified_pairwise.get_dataset(), self.allow_ties)

                from io.output.xmlwriter import XmlWriter
                classified_xmlwriter = XmlWriter(parallelsentences)
                classified_xmlwriter.write_to_file(filename_out + "xml")
                from io.output.wmt11tabwriter import Wmt11TabWriter
                classified_xmlwriter = Wmt11TabWriter(parallelsentences, "dfki_parseconf_%d" % i)
                classified_xmlwriter.write_to_file(filename_out + "tab")
                output.append("\n")
                print "".join(output)
    
    
    def rank_evaluate_and_print(self, test_xml, model):
        output = []
        test_dataset_pairwise = self.read_xml_data([test_xml])
        output.append("\t")
        for classifier in self.classifiers:
            if not classifier().__class__.__name__ in self.desired_classifiers:
                continue
            output.append(classifier().__class__.__name__)
            output.append("\t")
        output.append("\n")
        for attribute_names_string in model:
            output.append(attribute_names_string.replace(",", "\n"))
            output.append("\t")
            prev_attribute_names = []
            for (attribute_names, classifier) in  model[attribute_names_string]:
                if attribute_names != prev_attribute_names:
                    test_data_pairwise = OrangeData(test_dataset_pairwise, self.class_name, attribute_names, self.meta_attribute_names, True)
                prev_attribute_names = attribute_names
                
                #first pairwise scores with kendal tau
                (acc, taukendal) = test_data_pairwise.get_accuracy([classifier])
                #output.append(classifier.name)
                classified_pairwise = test_data_pairwise.classify_with(classifier)
                parallelsentences_multiclass = RankHandler().get_multiclass_from_pairwise_set(classified_pairwise.get_dataset(), self.allow_ties)
#                for ps in parallelsentences_multiclass:
#                    for tgt in ps.get_translations():
#                        print "%s\t%s" % (tgt.get_attribute("rank"), tgt.get_attribute("orig_rank")),
#                    print
                scoringset = Scoring(parallelsentences_multiclass)
                (rho, p) = scoringset.get_spearman_correlation("rank", "orig_rank")
                output.append("\t")
                output.append(str(rho))
                
                kendalltau = scoringset.get_kendall_tau("rank", "orig_rank")
                output.append("\t")
                output.append(str(kendalltau))
                
                #parallelsentences = classified_data.get_dataset().get_parallelsentences()
                output.append("\t")
                #output.append(str(acc))
                output.append(str(taukendal[0]))
                output.append(" | ")
            output.append("\n")
        print "".join(output)
            
            
                
    def train_evaluate(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_evaluate_and_print(self.test_filename, model)
    
    def train_decode(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_and_export(self.test_filename, self.output_filename, model)

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
            training = Training(config)
            #training.train_evaluate()
            training.train_decode()
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            
        
            
        
        