'''
Utilize the orange machine learning library
Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''

import cPickle as pickle
import sys
import os
import shutil
import tempfile

from ml.ranker import PairwiseRanker
from dataprocessor.ce.cejcml2orange import CElementTreeJcml2Orange
from dataprocessor.ce.cejcml import CEJcmlReader
from sentence.pairwiseparallelsentenceset import CompactPairwiseParallelSentenceSet

from Orange.data import Table
from Orange.data import Instance, Value, Domain
from Orange.evaluation.scoring import CA, Precision, Recall, F1 
from Orange.evaluation.testing import cross_validation
from Orange.classification.rules import rule_to_string
from Orange.classification.svm import get_linear_svm_weights
from Orange.classification import logreg

from Orange.classification.bayes import NaiveLearner
from Orange.classification.knn import kNNLearner
from Orange.classification.svm import SVMLearnerEasy as SVMEasyLearner
from Orange.classification.tree import TreeLearner
from Orange.classification.tree import C45Learner
from Orange.classification.logreg import LogRegLearner #,LibLinearLogRegLearner
from Orange.classification import Classifier 
from Orange.feature import Continuous
from support.preprocessing.jcml.align import target_attribute_names


def forname(name, **kwargs):
    """
    Pythonic way to initialize and return an orange learner. 
    Pass any parameters needed for the initialization
    @param name: the name of the learner to be returned
    @type name: string
    @return: an orange learner
    @rtype: Orange.classification.Classifier    
    """
    orangeclass = eval(name)
    return orangeclass(**kwargs)


def ranker_forname(name, **kwargs):
    """
    Return particular ranker class given a string
    @return: ranker object wrapping an Orange classifier
    @rtype: L{PairwiseRanker}
    """
    orangeclass = eval(name)
    return OrangeRanker(orangeclass(**kwargs))


def parallelsentence_to_instance(parallelsentence, domain=None):
    """
    Receive a parallel sentence and convert it into a memory instance for
    the machine learner. 
    @param parallelsentence:
    @type parallelsentence: L{ParallelSentence}
    @return: an orange instance    
    @type: C{Instance} from Orange.data
    """
    attributes = parallelsentence.get_nested_attributes()
    #print "attributes = ", attributes
    values = []
    
    #features required by the model need to be retrieved from the 
    #dic attributes containing feature values for this sentence
    #if domain: 
    #    feature_names = [feature.name for feature in domain.features]
    #else:
    #    feature_names = attributes.keys()
        #feature_type = feature.var_type
        
    for feature in domain.features:
        try:
            value = attributes[feature.name]
        except KeyError:
            sys.stderr.write("Feature '{}' not given by the enabled generators\n".format(feature.name))
            value = 0 

        #this casts the feature value we produced, in an orange value object
        orange_value = feature(value)
        values.append(orange_value)

    #create a model without the class value and use it for the new instance
    #@TODO: make it possible to initialize instance without having the domain
    classless_domain = Domain(domain.features, False)    
    instance = Instance(classless_domain, values)                                            
    return instance

    
def dataset_to_pairwise_instances(filename, 
                         attribute_set=None,
                         class_name=None,
                         reader=CEJcmlReader,                         
                         tempdir = "/tmp",
                         output_filename = None):
    """
    Receive a dataset filename and convert it into a memory table for the Orange machine learning
    toolkit. Since we need support for big data sets and optimal memory usage, the best way
    seems to create a temporary external tab separated file and load it directly with the Orange
    loader, which is implemented in C. This way no double object instances need to be on memory
    during conversion time.
    @param attribute_set: A description of the attributes we want to be included in the data table
    @type attribute_set: L{AttributeSet}
    @param class_name: The name of the class (label) for the machine learning task
    @type class_name: C{str}
    @param reader: A class which is able to read from external files. This give the possibility to 
    change the default reading behaviour (incremental XML reader) and read from other types of data files
    @type reader: L{DataReader} 
    @param tempdir: the temporary directory where the incremental file is written. Due to the
    increased I/O access, this is suggested to be in a storage unit that is locally connected to the
    computer that does the processsing, and not e.g. via NFS.
    @type tempdir: C{str}
    @param ouput_filename: specify here a full path if a copy of the Orange tab separated file needs to be
    retained (e.g. for debugging purposes)
    @type output_filename: C{str}
    @return An Orange Table object
    @rtype: C{Table}
    """
    
    #create a temporary file, to put the incremental output on the go
    temporary_filename = tempfile.mktemp(dir=tempdir, suffix='.tab')
    tabfile = open(temporary_filename, 'w')
    
    #get the text for the header of the orange file
    header = _get_pairwise_header(attribute_set, class_name)
    tabfile.write(header)
    
    #initialize the class that will take over the reading from the file
    dataset = reader(filename, compact=True, 
                     attribute_set=attribute_set)
    
    #iterate over all parallel sentences provided by the data reader
    for parallelsentence in dataset.get_parallelsentences():
        vectors = parallelsentence.get_vectors_product(attribute_set)
        
        #every parallelsentence has many instances
        for vector in vectors:
            tabline = "\t".join([str(value) for value in vector])
            print >>tabfile, tabline
    
    tabfile.close()
    
    datatable = Table(temporary_filename)
    
    if output_filename:
        #output file should be created only if the writing is finished
        shutil.copy(temporary_filename, output_filename)
    os.unlink(temporary_filename)
    return datatable
    
def _get_pairwise_header(self, attribute_names,
                      class_name):
    """
    Prepare the string that will be used for the orange tab file header
    @param parallel_attribute_names: the names of the attributes attached to the level of the parallel sentence
    @type parallel_attribute_names: [C{string}, ...]
    @param source_attribute_names: the names of the attributes of the source sentence
    @type source_attribute_names: [C{string}, ...]
    """
       
    #by default all attributes are continuous
    pairwise_attribute_names = attribute_names.get_names_pairwise()
    attribute_types = ['c']*len(pairwise_attribute_names)
    class_definition = ['']*len(pairwise_attribute_names)
    
    if class_name:
        #add class
        pairwise_attribute_names.append(class_name)
        attribute_types.append('d')
        class_definition.append('c')
    
    #convert python lists to string the efficient way
    line_names = "\t".join(pairwise_attribute_names)
    line_types = "\t".join(attribute_types)
    line_class = "\t".join(class_definition)
    
    #join three lines into one string
    header = "{}\n{}\n{}\n".format(line_names, line_types, line_class)
    return header
    

class OrangeRanker(PairwiseRanker):
    """
    This class represents a ranker implemented over pairwise orange classifiers. 
    This ranker is loaded into the memory from a dump file which contains an already trained
    model and provides functions to rank one source sentence + translations at a time
    @ivar fit: whether the classifier has been fit/trained or not
    @type fit: C{bool}
    @ivar learner: the un-trained classifier class to be used for training
    @type learner: C{Learner} from C{Orange.classification}
    @ivar classifier: the trained classifier object
    @type classifier: C{Classifier} from C{Orange.classification}
    """    
    
    def train(self, dataset_filename, **kwargs):
        datatable = dataset_to_pairwise_instances(filename=dataset_filename, **kwargs)
        self.learner = self.learner(**kwargs)
        self.classifier = self.learner(datatable)
        self.fit = True
    
    def _get_description(self, resultvector):
        output = []
        output.append("Used linear regression with Stepwise Feature Selection with the following weights")
        coefficients = logreg.dump(self.classifier)
        output.append(coefficients)
        
        output.append("\n\n")        
        output.append("domain: {}\n\n".format(self.classifier.domain))
        
        for resultentry in resultvector:
            system_names = resultentry['systems']
            value = resultentry['value']
            instance = resultentry['instance']
            distribution = resultentry['distribution']
            
        
            if value == -1:   
                output.append("System{} < System{}".format(system_names[0], system_names[1]))
            else:
                output.append("System{} > System{}".format(system_names[0], system_names[1]))
            output.append(" \n instance: {} \n probabilities: {}\n".format(instance, distribution))    
        return "".join(output)
    
    def get_ranked_sentence(self, parallelsentence):
        """
        Receive a parallel sentence with features and perform ranking
        @param parallelsentence: an object containing the parallel sentence
        @type parallelsentence: L{sentence.parallelsentence.ParallelSentence}    
        """
        
        #this will instruct orange to provide both binary decision and probability
        return_type = Classifier.GetBoth
        
        #follow the feature description as needed by the loaded classifier
        domain = self.classifier.domain
        
        #this is a clean-up fixing orange's bug, needed only for some classifiers
        #if self.classifier.__class__.__name__ in ["NaiveClassifier", "CN2UnorderedClassifier"]:
        #     orange_table = self.clean_discrete_features(orange_table)
        
        resultvector = []
        
        sys.stderr.write("source sentence before pairwising: '{}'".format(parallelsentence.get_source().get_string()))
        #de-compose multiranked sentence into pairwise comparisons
        pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences()
        
        #list that will hold the pairwise parallel sentences including the classifier's decision
        classified_pairwise_parallelsentences = []
        
        for pairwise_parallelsentence in pairwise_parallelsentences:
            #conver pairwise parallel sentence into an orange instance
            instance = parallelsentence_to_instance(pairwise_parallelsentence, domain=domain)
            
            #run classifier for this instance
            value, distribution = self.classifier(instance, return_type)

            sys.stderr.write("{}, {}, {}\n".format(pairwise_parallelsentence.get_system_names(), value, distribution))
            
            resultvector.append({'systems' : pairwise_parallelsentence.get_system_names(),
                                 'value' : (float(value.value)),
                                 'distribution': distribution,
                                 'instance' : instance})
            pairwise_parallelsentence.add_attributes({"rank_predicted":float(value.value),
                                                       "prob_-1":distribution[0],
                                                       "prob_1":distribution[1]
                                                       })
            
            classified_pairwise_parallelsentences.append(pairwise_parallelsentence)
        
        
        
        #gather all classified pairwise comparisons into one sentence again
        sentenceset = CompactPairwiseParallelSentenceSet(classified_pairwise_parallelsentences)
        ranked_sentence = sentenceset.get_multiranked_sentence("rank_predicted")
        return ranked_sentence, resultvector

    def rank_sentence(self, parallelsentence):
        ranked_sentence, resultvector = self.get_ranked_sentence(parallelsentence)
        result = [(t.get_attribute("rank"), t) for t in ranked_sentence.get_translations()]
#        return ranked_sentence.get_target_attribute_values("rank")
        description = self._get_description(resultvector)
        return result, description
        
        


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
    @type L{Orange.data.Table}
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
