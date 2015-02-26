"""

@author: Eleftherios Avramidis
"""
from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer
from wer import wer
from numpy import average
import logging as log

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
        target = target.get_string()
        try:
            ref = parallelsentence.get_reference().get_string()
        except:
            log.error("No reference. Aborting WER calculation")
            return {}
        #ef_tokens = PunktWordTokenizer().tokenize(ref_untokenized)
        #print ref_untokenized
        #print target_untokenized
        
        #target_tokens    =  " ".join(PunktWordTokenizer().tokenize(target_untokenized))
        wer_value = wer(target, [ref])
        return {'ref-wer': str(wer_value)}
        
    
    def analytic_score_sentences(self, sentence_tuples):
        return {'ref-wer': average([wer(h,[r]) for h,r in sentence_tuples])}
        
        
        
        
