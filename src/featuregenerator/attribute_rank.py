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

    def __init__(self, critical_attribute, new_attribute_name = None, reverse = False):
        '''
        @param critical_attribute The name of the attribute whose value will guide the ranking
        @type critical_attribute String
        @param new_attribute_name If the attributes needs to be renamed, the new name must be entered here. If not entered, then the attribute name is created based on the critical attribute, with the addition of the ending "-rank" 
        @type new_attribute_name String
        @param reverse Set True if you need it to be sorted on the reverse order
        @type boolean 
        '''
        self.critical_attribute = critical_attribute
        self.new_attribute_name = new_attribute_name
        self.reverse = reverse
        if not new_attribute_name:
            self.new_attribute_name = "%s-rank" % critical_attribute
        
        
        
    def add_features_parallelsentence(self, ps):
        values = [float(tgt.get_attribute(self.critical_attribute)) for tgt in ps.get_translations()]
        values = list(set(values))
        values = sorted(values)
        if self.reverse:
            values.reverse()	
        
        for translation in ps.get_translations():
            value = float(translation.get_attribute(self.critical_attribute))
            new_attribute_value = values.index(value) + 1
            translation.add_attribute(self.new_attribute_name, str(new_attribute_value))
        return ps
        
        
