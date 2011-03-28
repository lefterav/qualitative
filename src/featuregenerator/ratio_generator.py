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
        src_length = int(parallelsentence.get_source().get_attributes())
        tgt_length = len(PunktWordTokenizer().tokenize(sent_string))
        length_ratio = src_length / tgt_length
        simplesentence.add_attribute("length", str(tgt_length))
        simplesentence.add_attribute("length_ratio", str(length_ratio))
        return simplesentence
        