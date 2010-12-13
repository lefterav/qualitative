"""

@author: Eleftherios Avramidis
"""

from featuregenerator import FeatureGenerator

class LengthFeatureGenerator(FeatureGenerator):
    """
    classdocs
    """


    def get_features_sentence(self, simplesentence, parallelsentence):
        length = len( simplesentence.get_string() )
        attributes = {}
        attributes["length"] = str(length)
        return attributes
        
        
        