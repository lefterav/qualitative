"""

@author: Eleftherios Avramidis
"""

from featuregenerator import FeatureGenerator

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
        length = len(simplesentence.get_string().split(' ')) #count tokens
        return simplesentence.add_attribute("length", str(length))
    
    def add_features_tgt(self, simplesentence, parallelsentence):
        #get the length of the source
        src_length = int(parallelsentence.get_source().get_attribute("length"))
        tgt_length = len(simplesentence.get_string().split(' '))
        length_ratio = src_length / tgt_length
        simplesentence.add_attribute("length", str(tgt_length))
        simplesentence.add_attribute("length_ratio", str(length_ratio))
        