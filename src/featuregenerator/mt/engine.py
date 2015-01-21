'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from sentence.sentence import SimpleSentence
from featuregenerator.featuregenerator import FeatureGenerator

class MtEngine(FeatureGenerator):
    '''
    A generic abstract class for handling basic functions for an MT engine, to be extended
    by particular subclasses
    '''
    def __init__(self, source_language, target_language, **kwargs):
        self.source_language = source_language
        self.target_language = target_language 
        
        
    def traslate_string(self, string):
        raise NotImplementedError("This function needs to be implemented by an engine class")
    
    
    def add_features_parallelsentence(self, parallelsentence):
        """
        Receives the translation text in a wrapped source simple sentence object and returns translation and 
        features in a wrapped sentence object as well
        @param paralellesentence: the parallel sentence object that contains the text to be translated
        @type paralellesentence: ParallelSentence
        @return: the modified parallel sentence
        @rtype: ParallelSentence
        """
        
        translation_string, attributes = self.translate_string(parallelsentence.get_source().get_string())
        translation = SimpleSentence(translation_string, attributes)
        parallelsentence.tgt.append(translation)
        return parallelsentence
    
    
        
        
        
        