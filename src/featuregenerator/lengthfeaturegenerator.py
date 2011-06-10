"""

@author: Eleftherios Avramidis
"""
from featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer


class LengthFeatureGenerator(FeatureGenerator):
    """
    Class that provides a feature generator able to count the number of the tokens in the given simplesentences 
    """

            
    def get_features_simplesentence(self, simplesentence, parallelsentence = None):
        """
        Uses NLTK toolkit in order to tokenize given simplesentence and provide a feature with the number of tokens
        @param simplesentence: The SimpleSentence whose words are to be counted
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing lenght attribute 
        """
        sent_string = simplesentence.get_string().strip()
        length = len(PunktWordTokenizer().tokenize(sent_string)) #count tokens
        return {"length" : str(length)}
        
        