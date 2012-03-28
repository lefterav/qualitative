"""

@author: Eleftherios Avramidis
"""
from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet
from io_utils.input.xmlreader import XmlReader
from io_utils.output.xmlwriter import XmlWriter
from featuregenerator import FeatureGenerator
#from abc import ABCMeta
from sys import stderr

class LanguageFeatureGenerator(FeatureGenerator):
    """
    Extends the base FeatureGenerator class, by providing basic checking/functioning for language-specific feature processes.
    This way, this class can be inhereted and extended for feature categories that can only correspond to a particular language
    specified upon the initialization of the object
    @ivar lang: the language abrev. code
    @type lang: str
    """
    def __init__(self, lang):
        """
        In order to initialize a language-specific feature generator, the language needs to be instantiatied as a class variable
        @param lang: the language code of the language that the feature generator is capable of
        @type lang: string 
        """
        self.lang = lang
#        __metaclass__ = ABCMeta

    
    def get_features_src(self, simplesentence, parallelsentence):
        """
        Function that falls back to the general simple sentence feature generation, only if the language is supported by the feature generator 
        It receives a source simple sentence and returns a list of source features. 
        """

        attributes = {}
        src_lang = parallelsentence.get_attribute("langsrc") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.lang:
            attributes = self.get_features_simplesentence(simplesentence, parallelsentence)
        return attributes 

    def get_features_tgt(self, simplesentence, parallelsentence):
        """
        Function that falls back to the general simple sentence feature generation, only if the language is supported by the feature generator 
        It receives a target simple sentence and returns a list of target features. 
        """
        attributes = {}
        src_lang = parallelsentence.get_attribute("langtgt") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.lang:
            attributes = self.get_features_simplesentence(simplesentence, parallelsentence)
        return attributes 
    
    def get_features_simplesentence(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a simple sentence of any type and returns a list of features. 
        It should be overriden by a feature generator that doesn't differentiate between source and target features
        """
        #stderr.println("Featuregenerator of type %s doesn't provide SimpleSentence features" % self.__class__.__name__)
        
        return self.get_features_string(simplesentence.get_string())

    
    def add_features_dataset(self, dataset):
        """
        Augments the provided DataSet with features of the current feature generator. 
            It fires feature generation over the included parallelsentences it is composed of.
            It is not compatible with SAX parsing.
        @param dataset: The DataSet whose contents will be augmented
        @type dataset: sentence.dataset.DataSet
        @rtype: sentence.dataset.DataSet
        @return: The given DataSet augmented with features generated from the current featuregenerator 
        """
        parallelsentences = dataset.get_parallelsentences()
        #parallelsentences = [self.add_features_parallelsentence(parallelsentence) for parallelsentence in parallelsentences]
        self.add_features_batch(parallelsentences)
        print ".",
        return DataSet(parallelsentences)
    
    def add_features_batch(self, parallelsentences):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It allows the generation of features over many parallelsentences. 
        It is a flexible solution when feature generation doesn't take place item to item (see SAX parsing) but a whole list of parallel sentences needs
        to be implemented at once. In this case, feature generator may optimize better when the whole dataset is given. 
        @param parallelsentences: The parallel sentences to be be augmented
        @type parallelsentences: list(sentence.parallelsentence.ParallelSentence)
        @rtype: list(sentence.parallelsentence.ParallelSentence)
        @return: The given list of ParallelSentence which are now augmented with features generated from the current featuregenerator 
        """
        #Default function, if not overriden
        parallelsentences = [self.add_features_parallelsentence(parallelsentence) for parallelsentence in parallelsentences]

        return parallelsentences
    
    
    def get_features_string(self, string):
        raise NotImplementedError
    
    
    #TODO: remove this, as it breaks architecture    
    def add_features_batch_xml(self, filename_in, filename_out):
        reader = XmlReader(filename_in)
        parallelsentences = reader.get_parallelsentences()
        parallelsentences = self.add_features_batch(parallelsentences)
        reader = None
        writer = XmlWriter(parallelsentences)
        writer.write_to_file(filename_out)
        
        