"""
Interface for feature generators, i.e. classes which handle the 
generation of features over the parallel objects. Any new featuregenerator
should implement languagefeaturegenerator.py (if it is language-specific)
or featuregenerator.py  (it is language-generic).
"""
import importlib
import pkgutil
from featuregenerator import FeatureGenerator
import os
import logging as log
from _collections import defaultdict
import re

def get_feature_generators(feature_set):
    """
    Return the feature generators that are required to provide the features 
    in the given feature_name set 
    """
    dir = os.path.abspath(os.path.dirname(__file__))

    for subdir, _, _ in os.walk(dir):

        #import all feature generator modules
        for (_, name, _) in pkgutil.iter_modules([subdir]):
            print __package__
            try:
                importlib.import_module('.' + name, package=__package__)
            except Exception as e:
                log.warn(e)
            print __package__
        
        #get a list of those who report the attributes giveb
        generator_index = defaultdict(list)
        for cls in FeatureGenerator.__subclasses__():
            try:
                feature_names = cls.feature_names
            except:
                continue
            for feature_name in feature_names:
                if feature_name in feature_set.get_all_feature_names() or \
                True in [re.match(feature_name, att) for att in feature_set.get_all_feature_names()]:
                    generator_index[feature_name].append(cls)
    print generator_index
    


if __name__ == "__main__":
    get_feature_generators([])