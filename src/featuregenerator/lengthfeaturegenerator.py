"""

@author: Eleftherios Avramidis
"""
from __future__ import division
from featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer


class LengthFeatureGenerator(FeatureGenerator):
    """
    classdocs
    """


    #def get_features_sentence(self, simplesentence, parallelsentence):
        #length = len( simplesentence.get_string() )
        #attributes = {}
        
        #attributes["length"] = str(length)
        #return attributes
        
    def add_features_src(self, simplesentence, parallelsentence):
        sent_string = simplesentence.get_string().strip()
        length = len(PunktWordTokenizer().tokenize(sent_string)) #count tokens
        simplesentence.add_attribute("length", str(length))
        return simplesentence
    
    def add_features_tgt(self, simplesentence, parallelsentence):
        #get the length of the source
        sent_string = simplesentence.get_string().strip()
        src_length = int(parallelsentence.get_source().get_attribute("length"))
        tgt_length = len(PunktWordTokenizer().tokenize(sent_string))
        length_ratio = src_length / tgt_length
        simplesentence.add_attribute("length", str(tgt_length))
        simplesentence.add_attribute("length_ratio", str(length_ratio))
        return simplesentence
        