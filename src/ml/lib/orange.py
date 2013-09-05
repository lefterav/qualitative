'''
Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''

import cPickle as pickle

from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange 
from ml.classifier import Classifier

from sentence.dataset import DataSet
from sentence.pairwisedataset import AnalyticPairwiseDataset
from sentence.pairwiseparallelsentenceset import CompactPairwiseParallelSentenceSet

from Orange.data import Table
from Orange.data import Instance, Value, Domain
#from Orange.evaluation.scoring import CA, Precision, Recall, F1 
from Orange.evaluation.testing import cross_validation
from Orange.classification.rules import rule_to_string
from Orange.classification.svm import get_linear_svm_weights
from Orange.classification import logreg

#import Orange Learners
from Orange.classification.bayes import NaiveLearner
from Orange.classification.knn import kNNLearner
from Orange.classification.svm import SVMLearnerEasy as SVMEasyLearner
from Orange.classification.tree import TreeLearner
from Orange.classification.tree import C45Learner
from Orange.classification.logreg import LogRegLearner #,LibLinearLogRegLearner
from Orange.classification import Classifier
from Orange.feature import Continuous


def forname(name, **kwargs):
    """
    Pythonic way to initialize and return an orange learner. 
    Pass any parameters needed for the initialization
    """
    orangeclass = eval(name)
    return orangeclass(**kwargs)


def runtime_ranker_forname(name, **kwargs):
    orangeclass = eval(name)
    return OrangeRuntimeRanker(orangeclass(**kwargs))


def parallelsentence_to_instance(domain, parallelsentence):
    """
    Receive a parallel sentence and convert it into a memory instance for
    the machine learner. 
    @param parallelsentence:
    @type parallelsentence: L{sentence.parallelsentence.ParallelSentence}    
    """
    attributes = parallelsentence.get_nested_attributes()
    values = []
    
    #print "Attributes"
    #print attributes
    
    #print "Domain"
    #print domain
    
    domain_features = domain.features
    
    classless_domain = Domain(domain_features, False)
    
    #domain.get_metas()
    for feature in domain_features:
        feature_type = feature.var_type
        feature_name = feature.name
        
        #orange_variable = feature.get_value_from()
        try:
            value = attributes[feature_name]
        except KeyError:
            sys.exit("Feature '{}' not given by the enabled generators".format(feature_name))
        #orange_value = Value(orange_variable, str(value))
        orange_value = feature(value)
        values.append(orange_value)
    
    instance = Instance(classless_domain, values)                                            
    
    return instance
    
def dataset_to_instances(domain, dataset):
    """
    Receive a dataset and convert it into a memory table for the machine learner
    """
    for parallelsentence in dataset:
        instances = parallelsentence_to_instance(parallelsentence)
    return Table(instances) 


class OrangeRuntimeRanker:
    
    
    def __init__(self, classifier_filename):
        """
        Load previously trained classifier given existing filename
        @param classifier_filename: the filename which contains the trained classifier
        @type classifier_filename: str  
        """
        classifier_file = open(classifier_filename)
        self.classifier = pickle.load(classifier_file)
        classifier_file.close()
    
    def rank_sentence(self, parallelsentence):
        """
        Receive a parallel sentence with features and perform ranking
        @param parallelsentence: an object containing the parallel sentence
        @type parallelsentence: L{sentence.parallelsentence.ParallelSentence}    
        """
        return_type = Classifier.GetBoth
        
        domain = self.classifier.domain
        
#         if self.classifier.__class__.__name__ in ["NaiveClassifier", "CN2UnorderedClassifier"]:
#             orange_table = self.clean_discrete_features(orange_table)
        
        resultvector = []
        
        pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences()
        classified_pairwise_parallelsentences = []
        
        for pairwise_parallelsentence in pairwise_parallelsentences:
            instance = parallelsentence_to_instance(domain, pairwise_parallelsentence)
            value, distribution = self.classifier(instance, return_type)
            print pairwise_parallelsentence.get_system_names(), value, distribution
            resultvector.append((float(value.value), distribution))
            pairwise_parallelsentence.add_attributes({"rank_predicted":value,
                                                       "prob_-1":distribution[0],
                                                       "prob_1":distribution[1]
                                                       })
            
            classified_pairwise_parallelsentences.append(pairwise_parallelsentence)
            
        sentenceset = CompactPairwiseParallelSentenceSet(classified_pairwise_parallelsentences)
#        print "\n\nSentence set\n---\n", sentenceset       
        
        ranked_sentence = sentenceset.get_multiranked_sentence("rank_predicted")
#        print "\n\nRanked sent\n---\n", ranked_sentence.get_translations()
        result = [(t.get_attribute("system"),t.get_attribute("rank")) for t in ranked_sentence.get_translations()]
#        return ranked_sentence.get_target_attribute_values("rank")
        return result
        
        
                           
        
        
        
        
        
        


class OrangeClassifier(Classifier):
    '''
    Wrapper around an orange classifier object
    @ivar learner: the wrapped orange class
    @ivar training_data_filename: the jcml training file
    @type training_data_filename: str
    @ivar training_table: an Orange "table" of examples containing training instances
    @type \L{Orange.data.Table}
    @ivar model: the trained classifier
    @type model: Orange.classification.Classifier 
    @ivar test_data_filename: the jcml test file
    @type test_data_filename: str
    @ivar test_table: the Orange "table" of test examples
    @type \L{Orange.data.Table}
    '''
    def __init__(self, learner, **kwargs):
        '''
        Constructor.
        @param learner: an orange classifier whose functionality is to be wrapped 
        @type learner:  
        
        '''
        self.learner = learner(**kwargs)
        self.datafile = None
        self.training_data_filename = None
        self.training_table = None
        self.model = None
    
    
    
    def set_training_data(self, jcml_filename, 
                  class_name, 
                  desired_attributes,
                  meta_attributes,
                  
                  **kwargs):
        '''
        Read the data from an XML file, convert them to the proper format
        and remember its location
        @param jcml_filename: full path of the XML file where data reside
        @type jcml_filename: string
        @param class_name: name of class
        @type class_name: string
        @param desired_attributes: desired attributes
        @type desired_attributes: list of strings
        @param meta_attributes: meta attributes
        @type meta_attributes: list of strings
        '''
        
        output_file = jcml_filename.replace(".jmcl", ".tab")
        
        convertor = CElementTreeJcml2Orange(jcml_filename, 
                                         class_name, 
                                         desired_attributes, 
                                         meta_attributes, 
                                         output_file,
                                         compact_mode=True,
                                         **kwargs)
        
        convertor.convert()
        self.training_data_filename = output_file
        
    
    def load_training_data(self):
        '''
        Load the previously defined/converted training data in place
        '''
        self.training_table = Table(self.training_data_filename)
    
    def unload_training_data(self):
        '''
        Free up the memory occupied by the training data
        '''
        self.training_table = None
    
    
    def cross_validation_scores(self, folds=10):
        '''
        Perform cross validation on the training data.
        @param folds: number of cross-validation folds
        @type: int
        @return: the value of the classification accuracy
        @
        '''
        cv = cross_validation([self.learner], self.training_table, folds)        
        ca = CA(cv)
        return ca
    
    def train(self):
        self.model = self.learner(self.training_table)
        objectfile = self.training_data_filename.replace(".tab", ".clsf")
        pickle.dump(self.model, objectfile)
        

    #The following are algorithm-specific functions to write down details
    #about the produced model

    def _write_model_svm(self, basename):
        try:         
            weights = get_linear_svm_weights(self.model)
            textfilename = "{}.weights.txt".format(basename)
            f = open(textfilename, "w")
            f.write("Fitted parameters: \nnu = {0}\ngamma = {1}\n\nWeights: \n".format(self.model.fitted_parameters[0], self.model.fitted_parameters[1]))
            for weight_name, weight_value in weights.iteritems():
                f.write("{0}\t{1}\n".format(weight_name, weight_value))           
            f.close()
            return True
        except:
            return False
        
        
    def _write_model_rules(self, basename):
        try:
            rules = self.model.rules
            textfilename = "{}.rules.txt".format(basename)
            f = open(textfilename, "w")
            for r in rules:
                f.write("{}\n".format(rule_to_string(r)))             
            f.close()
            return 
        except:
            pass
        
        
    def _write_model_tree(self,basename):
        try:
            textfilename = "{}.tree.txt".format(basename)
            f = open(textfilename, "w")
            f.write(self.model.to_string("leaf", "node"))
            f.close()
            
            graphics_filename = "{}.tree.dot".format(basename)
            self.model.dot(graphics_filename, "leaf", "node")
        except:
            pass
        
   
    def write_model_description(self, basename):
        '''
        Method-specific functions for writing the model characteristics into a file
        @param basename: specify part of the filename which will be written 
        @type basename: string
        '''
        
        self._write_model_svm()
        self._write_model_rules()
           
        try:
            textfilename = "{}.logreg.dump.txt".format(basename)
            f = open(textfilename, 'w')
            f.write(logreg.dump(self.model))
            f.close()
        except:
            pass    
    
    
    def set_test_data(self, jcml_filename, 
                  class_name, 
                  desired_attributes,
                  meta_attributes,
                  output_file,
                  **kwargs):
        '''
        Read the data from an XML file, convert them to the proper format
        and remember its location
        @param jcml_filename: full path of the XML file where data reside
        @type jcml_filename: string
        @param class_name: name of class
        @type class_name: string
        @param desired_attributes: desired attributes
        @type desired_attributes: list of strings
        @param meta_attributes: meta attributes
        @type meta_attributes: list of strings
        '''
        
        convertor = CElementTreeJcml2Orange(jcml_filename, 
                                         class_name, 
                                         desired_attributes, 
                                         meta_attributes, 
                                         output_file,
                                         compact_mode=True,
                                         **kwargs)
        
        convertor.convert()
        self.test_data_filename = output_file
        
    def load_test_data(self):
        self.test_table = Table(self.test_data_filename)
    
    def unload_test_data(self):
        self.test_table = None
        
    def unload(self):
        self.unload_training_data()
        self.unload_test_data()
        self.model = None
