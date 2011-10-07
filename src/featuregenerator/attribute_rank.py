'''
Created on 07.10.2011

@author: Eleftherios Avramidis
'''
from featuregenerator import FeatureGenerator

class AttributeRankGenerator(FeatureGenerator):
    '''
    It produces a new ranking of the translated sentences, based on another value. 
    This "clean" ranking starts from zero and has a maximum ranking difference of 1 
    '''

    def __init__(self, critical_attribute, new_attribute_name):
        self.critical_attribute = critical_attribute
        self.new_attribute_name = new_attribute_name
        
    def add_features_parallelsentence(self, ps):
        values = [float(tgt.get_attribute(self.critical_attribute)) for tgt in ps.get_translations()]
        values = list(set(values))
        values = sorted(values)
        
        for translation in ps.get_translations():
            value = float(tgt.get_attribute(self.critical_attribute))
            new_attribute_value = values.index(value)
            translation.add_attribute(self.new_attribute_name, new_attribute_value)
        return ps
        
        