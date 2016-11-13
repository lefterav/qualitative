'''
Created on May 6, 2011

@author: Eleftherios Avramidis
'''
from Orange.classification.bayes import NaiveLearner as BayesLearner
from Orange.classification.knn import kNNLearner
from Orange.classification.svm import SVMLearnerEasy
#from orange import SVMClassifier
#from orange import SVMLearner
#from orngSVM import SVMLearnerEasy
#from orngTree import TreeLearner
#from orngLR import LogRegLearner
#from orange import kNNLearner
from io_utils.input.orangereader import OrangeData
from io_utils.input.xmlreader import XmlReader
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from sentence.scoring import Scoring
from featuregenerator.diff_generator import DiffGenerator
import sys
import ConfigParser
#from classifier.svmeasy import SVMEasy

 

class AutoRankingExperiment(object):
    '''
    classdocs
    '''

    def __init__(self, config = None, class_name = "rank"):
        '''
        Constructor
        '''
        self.classifiers = [BayesLearner] #, , SVMClassifier, TreeLearner, LogRegLearner, kNNLearner]
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
        
    def read_xml_data(self, filenames, allow_ties = False):
        allparallelsentences = []
        
        for filename in filenames:
            print "Reading XML %s " % filename
            parallelsentences = XmlReader(filename).get_parallelsentences()
            
            if self.convert_pairwise:
                parallelsentences = RankHandler().get_pairwise_from_multiclass_set(parallelsentences, allow_ties, self.exponential)

            if self.generate_diff:                 
                parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
            
            allparallelsentences.extend(parallelsentences)
            
#            cur_dataset = DataSet(parallelsentences)
#            
#            if not dataset:
#                dataset = cur_dataset
#            else:
#                dataset.append_dataset(cur_dataset)
        allparallelsentences = RankHandler().merge_overlapping_pairwise_set(allparallelsentences)
           
        #TODO: get list of attributes directly from feature generators

        return DataSet(allparallelsentences)
        
    def get_files(self, training_xml_filenames, test_xml_filename):
        training_dataset = self.read_xml_data(training_xml_filenames)
        test_dataset_pairwise = self.read_xml_data([test_xml_filename])
        attset = 0

        for attribute_names in self.attribute_sets:
            attset += 1
            orangefilename = "%s/training-attset%d.tab" % (self.orangefile, attset)
            OrangeData(training_dataset, self.class_name, [], self.meta_attribute_names, orangefilename)
            print "training data" , orangefilename
            
            orangefilename = "%s/test-attset%d.tab" % (self.orangefile, attset)
            OrangeData(test_dataset_pairwise, self.class_name, [], self.meta_attribute_names, orangefilename)

        

        

        
    
    def train_classifiers_attributes(self, training_xml_filenames):
        """
        Performs training of classifiers, uses them for ranking and evaluates the results on the fly
        @param training_data:
        @param test_data:
        """
        model = {}
        training_dataset = self.read_xml_data(training_xml_filenames)
        attset = 0
        for attribute_names in self.attribute_sets:
            model[",".join(attribute_names)] = []
            #convert data with only desired atts in orange format
            attset+=1
            orangefilename = "%s/training-attset%d.tab" % (self.orangefile, attset)
            training_data = OrangeData(training_dataset, self.class_name, attribute_names, self.meta_attribute_names, orangefilename)
            
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
        attset = 0
        for attribute_names_string in model:
            output.append(attribute_names_string.replace(",", "\n"))
            output.append("\t")
            prev_attribute_names = []
            i = 0
            
            for (attribute_names, classifier) in  model[attribute_names_string]:
                i = i+1
                if attribute_names != prev_attribute_names:
                    attset += 1
                    orangefilename = "%s/test-attset%d.tab" % (self.orangefile, attset)
                    test_data_pairwise = OrangeData(test_dataset_pairwise, self.class_name, attribute_names, self.meta_attribute_names, orangefilename)
                prev_attribute_names = attribute_names
                config
                #output.append(classifier.name)
                classified_pairwise = test_data_pairwise.classify_with(classifier)
                parallelsentences = RankHandler().get_multiclass_from_pairwise_set(classified_pairwise.get_dataset(), self.allow_ties)

                from io_utils.output.xmlwriter import XmlWriter
                classified_xmlwriter = XmlWriter(parallelsentences)
                classified_xmlwriter.write_to_file(filename_out + "xml")
                from io_utils.output.wmt11tabwriter import Wmt11TabWriter
                classified_xmlwriter = Wmt11TabWriter(parallelsentences, "dfki_parseconf_%d" % i)
                classified_xmlwriter.write_to_file(filename_out + "tab")
                output.append("\n")
                print "".join(output)
    
    def rank_sax_and_export(self, test_xml, filename_out, model, tab_filename, metric_name, lang_pair, test_set):
        for classifier in self.classifiers:
            if not classifier().__class__.__name__ in self.desired_classifiers:
                continue

        for attribute_names_string in model:
            #prev_attribute_names = []
            for (attribute_names, classifier) in  model[attribute_names_string]:
                input_file_object = open(test_xml, 'r')
                output_file_object = open(filename_out, 'w')
            
                from classifier.ranker import Ranker
                from io_utils.saxwmt11eval import SaxWMTexporter
                from xml.sax import make_parser
                
                ranker =  Ranker(classifier, attribute_names, self.meta_attribute_names)
                #proceed with parcing
                saxreader = SaxWMTexporter(output_file_object, [ranker], tab_filename, metric_name, lang_pair, test_set)
                myparser = make_parser()
                myparser.setContentHandler(saxreader)
                myparser.parse(input_file_object)
                input_file_object.close()
                output_file_object.close()
                

    def rank_sax_and_exportbest(self, test_xml, filename_out, model, tab_filename):
        for classifier in self.classifiers:
            if not classifier().__class__.__name__ in self.desired_classifiers:
                continue

        for attribute_names_string in model:
            #prev_attribute_names = []
            for (attribute_names, classifier) in  model[attribute_names_string]:
                input_file_object = open(test_xml, 'r')
                output_file_object = open(filename_out, 'w')
            
                from classifier.ranker import Ranker
                from io_utils.sax_bestrank2simplefile import SaxBestRank2SimpleFile
                from xml.sax import make_parser
                
                ranker =  Ranker(classifier, attribute_names, self.meta_attribute_names)
                #proceed with parcing
                saxreader = SaxBestRank2SimpleFile(output_file_object, [ranker], tab_filename)
                myparser = make_parser()
                myparser.setContentHandler(saxreader)
                myparser.parse(input_file_object)
                input_file_object.close()
                output_file_object.close()
    
    
    def rank_evaluate_and_print(self, test_xml, model):
        output = []
        test_dataset_pairwise = self.read_xml_data([test_xml], True)
        output.append("\t")
        for classifier in self.classifiers:
            if not classifier().__class__.__name__ in self.desired_classifiers:
                continue
            output.append(classifier().__class__.__name__)
            output.append("\t")
        output.append("\n")
        attset = 0
        for attribute_names_string in model:
            output.append(attribute_names_string.replace(",", "\n"))
            output.append("\t")
            prev_attribute_names = []
            for (attribute_names, classifier) in  model[attribute_names_string]:
                if attribute_names != prev_attribute_names:
                    attset += 1
                    orangefilename = "%s/test-attset%d.tab" % (self.orangefile, attset)
                    test_data_pairwise = OrangeData(test_dataset_pairwise, self.class_name, attribute_names, self.meta_attribute_names, orangefilename)
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
                
                accuracy, precision = scoringset.selectbest_accuracy("rank", "orig_rank") 
                
                #parallelsentences = classified_data.get_dataset().get_parallelsentences()
                output.append("\t")
                #output.append(str(acc))
                output.append(str(taukendal[0]))
                output.append("\t")
                output.append(str(accuracy))
                output.append(str(precision))
                
                output.append(" | ")
            output.append("\n")
        print " ".join(output)
            
            
                
    def train_evaluate(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_evaluate_and_print(self.test_filename, model)
    
    def train_decode(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_and_export(self.test_filename, self.output_filename, model)
        
        
    def train_decodebest(self):
        model = self.train_classifiers_attributes(self.training_filenames)
        self.rank_sax_and_exportbest(self.test_filename, self.output_filename, model, self.output_filename+".tab")
        
        
    def print_system_score(self, filename, rank_attribute):
        self.convert_pairwise = False
        test_dataset = self.read_xml_data([filename])
        scoringset = Scoring(test_dataset.get_parallelsentences())
        systemscores = scoringset.get_systems_scoring_from_segment_ranks(rank_attribute)
        
        entry = ["dfki_parseconf\tde-en\twmt11combo\t%s\t%%01.4f\n" % (system_name, systemscores[system_name]) for system_name in systemscores ]
        return entry    


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
            
        
            
        
        
