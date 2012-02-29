"""

@author: Eleftherios Avramidis
"""
from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet
from io.input.xmlreader import XmlReader
from io.output.xmlwriter import XmlWriter
#from abc import ABCMeta
from sys import stderr

class FeatureGenerator():
    """
    A base feature generator class, with no particular functioning. 
        It just provides basic feature generator functions to be inherited (or overwritten) by specific feature generators.
        If you want to code a new FeatureGenerator, it must inherit this class and override one or all of the methods 
        get_features_src, get_features_tgt, get_features_simplesentence, get_features_parallelsentence 
    """
#    def __init__(self):
#        pass
#        __metaclass__ = ABCMeta
#
    
    def add_features_parallelsentence(self, parallelsentence):
        """
        Augments the provided ParallelSentence with features of the current feature generator. 
            It fires feature generation functions over the included simplesentences it is composed of.
        @param parallelsentence: The ParalleSentence whose contents will be augmented
        @type parallelsentence: sentence.parallelsentence.ParalleSentence
        @rtype: sentence.parallelsentence.ParalleSentence
        @return: The given ParalleSentence augmented with features generated from the current featuregenerator 
        """                
        src = self.add_features_src (parallelsentence.get_source(), parallelsentence)
        tgt = [(self.add_features_tgt (tgt_item, parallelsentence)) for tgt_item in parallelsentence.get_translations()]
        try:
            ref = self.add_features_tgt (parallelsentence.get_reference(), parallelsentence)
        except:
            ref = parallelsentence.get_reference()
        
        #recreate the parallelsentence with the augmented contents
        parallelsentence = ParallelSentence(src, tgt, ref, parallelsentence.get_attributes()) 
        #add the attributes of the parallelsentence   
        parallelsentence.add_attributes (self.get_features_parallelsentence(parallelsentence))
        return parallelsentence

    def add_features_src(self, simplesentence, parallelsentence = None):
        """
        Gets a source SimpleSentence and (optionally) its corresponding Parallelsentence and returns a SimpleSentence with the generated features
            Operates as a wrapper around the get_features_src method, which returns a dictionary with the generated features. 
            From it we receive the dictionary, we duplicate the source SimpleSentence object and we return a proper source SimpleSentence object containing the generated features.
        @param simplesentence: The source sentence of a ParallelSentence
        @type simplesentence: sentence.sentence.SimpleSentence 
        @param parallelsentence: The parallelsentence containing the given source sentence. Can be omitted if the subclassed feature generator doesn't require the parallelsentence in order to deliver source features
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @rtype: sentence.sentence.SimpleSentence 
        @return: A source SimpleSentence object similar to the one given, but now containing the generated features.
        """
        simplesentence = deepcopy(simplesentence)
        simplesentence.add_attributes(self.get_features_src(simplesentence, parallelsentence))
        return simplesentence
        
    def add_features_tgt(self,simplesentence, parallelsentence = None):
        """
        Gets a target SimpleSentence and (optionally) its corresponding Parallelsentence and returns a SimpleSentence with the generated features
            Operates as a wrapper around the get_features_src method, which returns a dictionary with the generated features. 
            From it we receive the dictionary, we duplicate the target SimpleSentence object and we return a proper target SimpleSentence object containing the generated features.
        @param simplesentence: The target sentence of a ParallelSentence
        @type simplesentence: sentence.sentence.SimpleSentence 
        @param parallelsentence: The parallelsentence containing the given target sentence. Can be omitted if the subclassed feature generator doesn't require the parallelsentence in order to deliver target features
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @rtype: sentence.sentence.SimpleSentence 
        @return: A target SimpleSentence object similar to the one given, but now containing the generated features.
        """
        simplesentence = deepcopy(simplesentence)
        simplesentence.add_attributes(self.get_features_tgt(simplesentence, parallelsentence))
        return simplesentence
    
    def add_features_simplesentence(self, simplesentence, parallelsentence = None):
        """
        Works as a generalized method covering the functionality of both add_features_src and add_features_tgt. It gets a SimpleSentence of any origin (source/target etc.) and (optionally) its corresponding Parallelsentence and returns a SimpleSentence with the generated features
            Operates as a wrapper around the get_features_src method, which returns a dictionary with the generated features. 
            From it we receive the dictionary, we duplicate the SimpleSentence object and we return a proper SimpleSentence object containing the generated features.
        @param simplesentence: A simplesentence
        @type simplesentence: sentence.sentence.SimpleSentence 
        @param parallelsentence: The parallelsentence containing the given SimpleSentence. Can be omitted if the subclassed feature generator doesn't require the parallelsentence in order to deliver simplesentence features
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @rtype: sentence.sentence.SimpleSentence 
        @return: A SimpleSentence object similar to the one given, but now containing the generated features.
        """
        simplesentence = deepcopy(simplesentence)
        simplesentence.add_attributes(self.get_features_simplesentence(simplesentence, parallelsentence))
        return simplesentence
    
    def get_features_parallelsentence(self, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a parallel sentence and returns a list of parallel sentence features that globally describe the parallel sentence itself. 
        Features that describe source or target sentence etc should be added in functions get_features_src and get_features_tgt declared below. 
        Implementation here provides an empty dictionary, in case subclassed feature generator doesn't provide any features.
        """
        #stderr.write("Featuregenerator of type %s doesn't provide global ParallelSentence features\n" % self.__class__.__name__)
        return {}
    
    def get_features_src(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a source simple sentence and returns a list of source features. 
        Implementation here fallbacks to the get_features_simplesentence function, when feature generator doesn't differentiate between source and target features
        """
        return self.get_features_simplesentence(simplesentence, parallelsentence)

    def get_features_tgt(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a target simple sentence and returns a list of target features. 
        Implementation here fallbacks to the get_features_simplesentence function, when feature generator doesn't differentiate between source and target features
        """
        return self.get_features_simplesentence(simplesentence, parallelsentence)
    
    def get_features_simplesentence(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a simple sentence of any type and returns a list of features. 
        It should be overriden by a feature generator that doesn't differentiate between source and target features
        """
        #stderr.println("Featuregenerator of type %s doesn't provide SimpleSentence features" % self.__class__.__name__)
        return {}
    
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
        parallelsentences = self.add_features_batch(parallelsentences)
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
    
    def get_annotation_name(self):
        """
        Provides a name describing the set of features that each particular annotator added. 
        If not overriden, generates a name out of the class name
        @return the name of the annotation
        @rtype string
        """
        name = self.__class__.__name__
        if name.endswith("FeatureGenerator"):
            name = name[0:len(name)-len("FeatureGenerator")].lower()
        
    
    #TODO: remove this, as it breaks architecture    
#    def add_features_batch_xml(self, filename_in, filename_out):
#        reader = XmlReader(filename_in)
#        parallelsentences = reader.get_parallelsentences()
#        parallelsentences = self.add_features_batch(parallelsentences)
#        reader = None
#        writer = XmlWriter(parallelsentences)
#        writer.write_to_file(filename_out)
    

    
    def process_dataset(self, dataset):
        return self.add_features_dataset(dataset)
        