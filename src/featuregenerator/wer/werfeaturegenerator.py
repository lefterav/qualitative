"""

@author: Eleftherios Avramidis
"""
from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer
from wer import wer

class WERFeatureGenerator(FeatureGenerator):
    """
    Class that provides a feature generator able to count the number of the tokens in the given simplesentences 
    sudo apt-get install python all dev
    sudo pypi-install python-Levenshtein
    """


        
    
    def get_features_tgt(self, target, parallelsentence):
        """
        Calculates word error rate for the given target sentence, against the reference sentence
        @param simplesentence: The target sentence to be scored
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing lenght attribute 
        """
        target_untokenized = target.get_string()
        ref_untokenized = parallelsentence.get_reference().get_string()
        ref_tokens = PunktWordTokenizer().tokenize(ref_untokenized)
        #print ref_untokenized
        #print target_untokenized
        
        target_tokens    =  " ".join(PunktWordTokenizer().tokenize(target_untokenized))
        wer_value = wer(target_tokens, [ref_tokens])
        return {'wer': str(wer_value)}
        
        
        
        
        
        
