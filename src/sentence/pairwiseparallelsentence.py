#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin
'''


from parallelsentence import ParallelSentence 
from copy import deepcopy



class PairwiseParallelSentence(ParallelSentence):

    def __init__(self, source, translations, systems, reference=None, attributes={}):
        """
        Constructor
        @type source: SimpleSentence
        @param source: the source text of the parallel sentence
        @type translations: tuple of translations (SimpleSentence, SimpleSentence)
        @param translations: a pair of translations
        @type reference: SimpleSentence 
        @param reference: The desired translation provided by the system
        @type attributes: dict { String name , String value }
        @param the attributes: that describe the parallel sentence
        @type systems: tuple of strings
        @param systems: names of target systems
        """
        self.src = source 
        self.tgt = translations
        self.systems = systems
        self.ref = reference
        self.attributes = deepcopy (attributes)
        
    def get_system_names(self):
        return self.systems
    
    def get_translations(self):
        return self.tgt
