"""

@author: Eleftherios Avramidis
"""
from __future__ import division
from featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer


class RatioGenerator(FeatureGenerator):
    """
    Computes tgt/source ratios for features with the same name
    """


    #def get_features_sentence(self, simplesentence, parallelsentence):
        #length = len( simplesentence.get_string() )
        #attributes = {}
        
        #attributes["length"] = str(length)
        #return attributes
        

    
    def add_features_tgt(self, simplesentence, parallelsentence):
        #get the length of the source
        tgt_attributes = simplesentence.get_attributes()
        src_attributes = parallelsentence.get_source().get_attributes()
        
        #if there are two features with the same name in bot src and target, calculate their ratio and add it
        for tgt_attribute_name in tgt_attributes.keys():
            if tgt_attribute_name in src_attributes.keys():
                try:
                    new_attribute_name = "%s_ratio" % tgt_attribute_name
                    if new_attribute_name not in tgt_attributes.keys():
                        #do calculations only if needed
                        tgt_attribute_value = float(tgt_attributes[tgt_attribute_name])
                        src_attribute_value = float(src_attributes[tgt_attribute_name])
                        if tgt_attribute_value == 0:
                            ratio = float('inf')
                        else:
                            ratio = 1.0 * src_attribute_value / tgt_attribute_value
                        simplesentence.add_attribute(new_attribute_name, str(ratio))
                except ValueError:
                    pass
                    
                    
        return simplesentence
        