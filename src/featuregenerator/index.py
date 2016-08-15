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

from .featuregenerator import FeatureGenerator
from .languagefeaturegenerator import LanguageFeatureGenerator


class FeatureGeneratorManager(object):
    
    def __init__(self):
        self._import_feature_generators()
        self._index_feature_generators()

    def _import_feature_generators(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
    
        for _, name, _ in pkgutil.walk_packages(path=[package_dir],
                                                          prefix='featuregenerator.',
                                                          onerror=lambda x: None):
            try:
                print name
                importlib.import_module(name, package="featuregenerator")
            except Exception as e:
                log.warn(e)
                
    
    def _index_feature_generators(self):
        """
        Return the feature generators that are required to provide the features 
        in the given feature_name set 
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
        generators = []
        try:
            requirements = generator.requirements
        except AttributeError:
            return []
        
        for requirement in requirements:
            req_generators = self.get_feature_generators([requirement])
            generators.extend(req_generators)
        
        return generators
                    
    
    def get_feature_generators(self, feature_set):
        selected_generators = []
        for feature_name in feature_set:
            # if the feature is provided by some generators add them to the list
            
            for generator in self.generator_index[feature_name]:
                selected_generators.extend(self._get_requirements(generator))
                selected_generators.append(generator)
            
            for pattern, matched_generators in self.generator_patterns:
                if re.match(pattern, feature_name):
                    for generator in matched_generators:
                        selected_generators.extend(self._get_requirements(generator))
                        selected_generators.append(generator)
        
        #remove duplicates but keep list sorted
        appeared_generators = set()
        shortened_generators = []
        for generator in selected_generators:
            if generator not in appeared_generators:
                appeared_generators.add(generator)
                shortened_generators.append(generator)
        
        return shortened_generators
    
    
    def _initialize_from_config(self, generator, section_name, config, gateway, language):
        try:
            params = dict(config.items(section_name))
        except:
            params = {}
        
        params['gateway'] = gateway
        params['language'] = language
        return [generator(**params)]
        
    
    def initialize_given_feature_generators(self, feature_generators, config, source_language, target_language, gateway):
        
        initialized_generators = []
        for generator in feature_generators:
            if generator.is_bilingual:
                
                section_name = "{}:{}-{}".format(generator.__name__.replace("FeatureGenerator", ""), 
                                                 source_language, target_language)
                try:
                    params = dict(config.items(section_name))
                except:
                    params = {}
                inverted_section_name = "{}:{}-{}".format(generator.__name__.replace("FeatureGenerator", ""), 
                                                          target_language, source_language)
                inverted_model = config.get(inverted_section_name, "model")
                initialized_generator = generator(gateway=gateway, 
                                                  source_language=source_language, 
                                                  target_language=target_language, 
                                                  inverted_model=inverted_model,
                                                  **params)
                initialized_generators.append(initialized_generator)                
                
            elif generator.is_language_specific:
                for language in [source_language, target_language]:
                    section_name = "{}:{}".format(generator.__name__.replace("FeatureGenerator", ""), language)                    
                    initialized_generators.extend(self._initialize_from_config(generator, section_name, config, gateway, language))
            else:
                section_name = "{}".format(generator.__name__.replace("FeatureGenerator", ""))
                initialized_generators.extend(self._initialize_from_config(generator, section_name, config, gateway, language))
        return initialized_generators                
            