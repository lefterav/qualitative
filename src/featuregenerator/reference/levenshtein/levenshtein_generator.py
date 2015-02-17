'''
Feature generator for Levenshtein distance (reference-aware evaluation metric)
Created on 07.10.2011

@author: Eleftherios Avramidis
'''
from featuregenerator.featuregenerator import FeatureGenerator
from levenshtein import levenshtein_tok
from numpy.lib.function_base import average

class LevenshteinGenerator(FeatureGenerator):
    '''
    Produce attribute from Levenshtein Distance
    '''


    def get_features_tgt(self, target, parallelsentence):
        """
        Calculates Levenshtein distance for the given target sentence, against the reference sentence
        @param simplesentence: The target sentence to be scored
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing Levenshtein distance as an attribute 
        """
        target_untokenized = target.get_string()
        try:
            ref_untokenized = parallelsentence.get_reference().get_string()
        

            wer_value = levenshtein_tok(target_untokenized, ref_untokenized)
            return {'ref-lev': str(wer_value)}
        except:
            return {}
        

    def analytic_score_sentences(self, sentence_tuples):
        return {'ref-lev': average([levenshtein_tok(h, r) for h, r in sentence_tuples])} 