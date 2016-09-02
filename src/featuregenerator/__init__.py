"""
Interface for feature generators, i.e. classes which handle the 
generation of features over the parallel objects. Any new featuregenerator
should implement languagefeaturegenerator.py (if it is language-specific)
or featuregenerator.py  (it is language-generic).
"""

'''
Created on Jul 28, 2016

@author: lefterav
'''
from collections import defaultdict
import importlib
import logging as log
import os
import pkgutil
import re
from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet
from dataprocessor.input.xmlreader import XmlReader
from dataprocessor.output.xmlwriter import XmlWriter
#from abc import ABCMeta
from sys import stderr

from copy import deepcopy
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet
from dataprocessor.input.xmlreader import XmlReader
from dataprocessor.output.xmlwriter import XmlWriter
from collections import OrderedDict
#from abc import ABCMeta
from sys import stderr

class FeatureGenerator(object):
    """
    A base feature generator class, with no particular functioning. 
    It just provides basic feature generator functions to be inherited (or overwritten) by specific feature generators.
    If you want to code a new FeatureGenerator, it must inherit this class and override one or all of the methods 
    get_features_src, get_features_tgt, get_features_simplesentence, get_features_parallelsentence 
    """
    is_bilingual = False
    is_language_specific = False
    
    def __init__(self, **params):
        pass
    
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
        @param parallelsentence: An instance of parallel sentence whose features will be extracted
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @return: the attributes extracted by the analysis process
        @rtype: dict
        """
        #stderr.write("Featuregenerator of type %s doesn't provide global ParallelSentence features\n" % self.__class__.__name__)
        return {}
    
    def get_features_src(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a source simple sentence and returns a list of source features. 
        Implementation here fallbacks to the get_features_simplesentence function, when feature generator doesn't differentiate between source and target features
        @param simplesentence: An instance of the source sentence whose features will be extracted
        @type simplesentence: sentence.sentence.SimpleSentence
        @param parallelsentence: An instance of parallel sentence whose features will be extracted
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @return: the attributes extracted by the analysis process
        @rtype: dict
        """
        return self.get_features_simplesentence(simplesentence, parallelsentence)

    def get_features_tgt(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a target simple sentence and returns a list of target features. 
        Implementation here fallbacks to the get_features_simplesentence function, when feature generator doesn't differentiate between source and target features
        @param simplesentence: An instance of the target sentence whose features will be extracted
        @type simplesentence: sentence.sentence.SimpleSentence
        @param parallelsentence: An instance of parallel sentence whose features will be extracted
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @return: the attributes extracted by the analysis process
        @rtype: dict
        """
        return self.get_features_simplesentence(simplesentence, parallelsentence)
    
    def get_features_simplesentence(self, simplesentence, parallelsentence):
        """
        Abstract method to be overriden by the particular subclassed feature generator. 
        It receives a simple sentence of any type and returns a list of features. 
        It should be overriden by a feature generator that doesn't differentiate between source and target features
        @param simplesentence: An instance of a simple sentence whose features will be extracted
        @type simplesentence: sentence.sentence.SimpleSentence
        @param parallelsentence: An instance of parallel sentence whose features will be extracted
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @return: the attributes extracted by the analysis process
        @rtype: dict
        """
        #stderr.println("Featuregenerator of type %s doesn't provide SimpleSentence features" % self.__class__.__name__)
        return self.get_features_string(simplesentence.string)
    
    def get_features_string(self, string):
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
        """
        Abstract method to be overriden by the particular subclassed feature generator,
        when an entire dataset needs to be processed as a whole.
        @param dataset: a dataset containing many parallel sentences
        @type dataset: sentence.dataset.DataSet
        @return dataset: the given dataset annotated
        @rtype: sentence.dataset.DataSet
        """
        return self.add_features_dataset(dataset)




class LanguageFeatureGenerator(FeatureGenerator):
    """
    Extends the base FeatureGenerator class, by providing basic checking/functioning for language-specific feature processes.
    This way, this class can be inhereted and extended for feature categories that can only correspond to a particular language
    specified upon the initialization of the object
    @ivar language: the language abrev. code
    @type language: str
    """
    is_language_specific = True
    
    def __init__(self, language):
        """
        In order to initialize a language-specific feature generator, the language needs to be instantiatied as a class variable
        @param language: the language code of the language that the feature generator is capable of
        @type language: string 
        """
        self.language = language
#        __metaclass__ = ABCMeta

    
    def get_features_src(self, simplesentence, parallelsentence):
        """
        Function that falls back to the general simple sentence feature generation, only if the language is supported by the feature generator 
        It receives a source simple sentence and returns a list of source features. 
        """

        attributes = OrderedDict()
        src_lang = parallelsentence.get_attribute("langsrc") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.language:
            attributes = self.get_features_simplesentence(simplesentence, parallelsentence)
        return attributes 

    def get_features_tgt(self, simplesentence, parallelsentence):
        """
        Function that falls back to the general simple sentence feature generation, only if the language is supported by the feature generator 
        It receives a target simple sentence and returns a list of target features. 
        """
        attributes = OrderedDict()
        src_lang = parallelsentence.get_attribute("langtgt") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.language:
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
        
        
        
class FeatureGeneratorManager(object):
    '''
    It manages all the implemented feature generators so that they 
    can be loaded in a dynamic way based on the demands of modifiable 
    annotation pipelines
    @ivar generator_index: It maps every feature name to the feature generators
    that produce this feature  
    @type generator_index: {C{str}: [L{FeatureGenerator}, ...], ...} 
    @ivar generator_patterns: A list of tuples, where every feature name regex
    is mapped to the feature generators that produced the features whose name 
    matches that regex
    @type generator_patterns: [(C{str}, [L{FeatureGenerator}, ...]), ...]
    '''
    
    def __init__(self):
        self._import_feature_generators()
        self._index_feature_generators()

    def _import_feature_generators(self):
        """
        Import all available modules in the package featuregenerator
        """
        package_dir = os.path.abspath(os.path.dirname(__file__))
    
        for _, name, _ in pkgutil.walk_packages(path=[package_dir],
                                                prefix='featuregenerator.',
                                                onerror=lambda x: None):
            try:
                importlib.import_module(name, package="featuregenerator")
            except Exception as e:
                log.warn(e)
                
    
    def _index_feature_generators(self):
        """
        Organize the feature generators so that they can be looked up. 
        A dictionary maps every feature to the generators it gets produced by.
        Additionally, a list of tuples associates feature name patterns with
        the respective generators. Both data structures remain loaded as class 
        variables
        """
                        
        #get a list of those who report the attributes given
        self.generator_index = defaultdict(list)    
        self.generator_patterns = []
        
        #get a list of the featuregenerator subclasses and their antecedents
        generators = FeatureGenerator.__subclasses__()
        generators.extend(LanguageFeatureGenerator.__subclasses__())
    
        second_level_subclasses = []
        for generator in generators:
            second_level_subclasses.extend(generator.__subclasses__())        
        generators.extend(second_level_subclasses)
        
        for generator in generators:

            #get the feature names provided by this generator
            try:
                feature_names = generator.feature_names
            except AttributeError:
                feature_names = []
            
            for feature_name in feature_names:
                self.generator_index[feature_name].append(generator)
                
            #get the feature_patterns provided by this generator
            try:
                feature_patterns = generator.feature_patterns
            except AttributeError:
                feature_patterns = []
            
            for feature_pattern in feature_patterns:
                self.generator_patterns.append((feature_pattern, [generator]))
            
    
    def _get_requirements(self, generator):
        """
        Function for the recursion to get the requirements for generators
        @param generator: the feature generator whose requirements need to be resolved
        @type generator: L{FeatureGenerator}
        @return: a list of generators who are requirements for the given generator
        @rtype: [L{FeatureGenerator}, ...]
        """
        generators = []
        try:
            requirements = generator.requirements
        except AttributeError:
            return []
        
        for requirement in requirements:
            req_generators = self.get_feature_generators([requirement])
            generators.extend(req_generators)
        
        return generators
                    
    
    def get_feature_generators(self, feature_names):
        """
        Return the feature generators that are required to provide the features 
        in the given feature_name set 
        @param feature_names: a list of the features whose generators are needed
        @type feature_names: C{str}
        @return: the non-initialized classes of the required feature generators
        @rtype: [L{Featuregenerator}, ...]        
        """
        selected_generators = []
        for feature_name in feature_names:
            # if the feature is provided by some generators add them to the list
            
            for generator in self.generator_index[feature_name]:
                required_generators = self._get_requirements(generator)
                selected_generators.extend(required_generators)
                log.debug("Adding requirements for generator {}: {}".format(generator, required_generators))
                selected_generators.append(generator)
            
            for pattern, matched_generators in self.generator_patterns:
                if re.match(pattern, feature_name):
                    for generator in matched_generators:
                        required_generators = self._get_requirements(generator)
                        selected_generators.extend(required_generators)
                        log.debug("Adding requirements for generator {}: {}".format(generator, required_generators))
                        selected_generators.append(generator)
        
        #remove duplicates but keep list sorted
        appeared_generators = set()
        shortened_generators = []
        log.debug("Selected generators: {}".format(selected_generators))
        for generator in selected_generators:
            if generator not in appeared_generators:
                appeared_generators.add(generator)
                shortened_generators.append(generator)
        log.debug("Shortened generators list: {}".format(shortened_generators))
        return shortened_generators
    
    
    def _initialize_from_config(self, generator, section_name, config, gateway, language):
        try:
            params = dict(config.items(section_name))
        except:
            params = {}
        
        params['gateway'] = gateway
        params['language'] = language
        log.info("Feature generator manager initializing {} for {} with params {}...".format(generator.__name__, language, params))
        initialized_generator = generator(**params)
        log.info("Feature generator manager successfully initialized {} for {}.".format(generator.__name__, language))
        return initialized_generator
        
    
    def initialize_given_feature_generators(self, feature_generators, config, language, gateway, source_language=None):
        """
        Given a list of feature generator classes and a configuration file, 
        initialize them as feature generator instances  
        """
        initialized_generators = []
        for generator in feature_generators:
            if generator.is_bilingual and source_language:
                section_name = "{}:{}-{}".format(generator.__name__.replace("FeatureGenerator", ""),
                                                 source_language, language)
                try:
                    params = dict(config.items(section_name))
                except:
                    params = {}
                if config.has_option(section_name, "model"):
                    inverted_section_name = "{}:{}-{}".format(generator.__name__.replace("FeatureGenerator", ""), 
                                                              language, source_language)
                    inverted_model = config.get(inverted_section_name, "model")
                    initialized_generator = generator(gateway=gateway, 
                                                      source_language=source_language, 
                                                      language=language, 
                                                      inverted_model=inverted_model,
                                                      **params)
                else:
                     initialized_generator = generator(gateway=gateway, 
                                                      source_language=source_language, 
                                                      language=language, 
                                                      **params)

                initialized_generators.append(initialized_generator)                
                
            elif generator.is_language_specific:                
                section_name = "{}:{}".format(generator.__name__.replace("FeatureGenerator", ""), language)                    
                initialized_generators.append(self._initialize_from_config(generator, section_name, config, gateway, language))
            else:
                section_name = "{}".format(generator.__name__.replace("FeatureGenerator", ""))
                initialized_generators.append(self._initialize_from_config(generator, section_name, config, gateway, language))
        return initialized_generators  
    
    def initialize_feature_generators(self, featurelist, config, language, gateway, source_language=None):
        featuregenerator_classes = self.get_feature_generators(featurelist)
        return self.initialize_given_feature_generators(featuregenerator_classes, config, language, gateway, source_language)

    def get_parallel_features_pipeline(self, featureset, config, source_language, target_language, gateway):
        """
        Prepares the full pipeline for feature generation on source, targets and references
        @param featureset: a FeatureSet instance, containing the names of source, target and reference features
        @type featureset: L{sentence.parallelsentence.FeatureSet}
        @param config: a ConfigParser object containing the parameters for the language resources
        @type config: C{ConfigParser}
        @param source_language: the language code of the source language
        @type source_language: C{str}
        @param target_language: the language code of the target language
        @type target_language: C{str}
        @param gateway: a Py4J gateway object, necessary for loading Java feature generators
        @type gateway: L{LocalGateway}
        @return: a tuple of the initialized feature generators for source, target and reference
        @rtype: tuple with 3 lists of L{FeatureGenerator} subclasses
        """
        #TODO: solve the issue that some language agnostic generators will be 
        #initialized for both source and target -- or maybe its not a big issue cause they oftern are
        #not expensive              
        source_featuregenerators = self.initialize_feature_generators(featureset.source_attribute_names, config,
                                                                      source_language, gateway, source_language=None)
        target_featuregenerators = self.initialize_feature_generators(featureset.target_attribute_names, config,
                                                                      target_language, gateway, source_language=source_language)        
        reference_featuregenerators = self.initialize_feature_generators(featureset.ref_attribute_names, config, target_language, 
                                                                         gateway, source_language=source_language)
    
        return source_featuregenerators, target_featuregenerators, reference_featuregenerators
            
