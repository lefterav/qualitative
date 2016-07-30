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

        generators = FeatureGenerator.__subclasses__()
        generators.extend(LanguageFeatureGenerator.__subclasses__())
        
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