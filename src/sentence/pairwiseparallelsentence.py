#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin
'''


from parallelsentence import ParallelSentence 
from copy import deepcopy



class PairwiseParallelSentence(ParallelSentence):
    """
    A pairwise parallel sentence, is a parallel sentence that contains output produced by only two systems.  
    """

    def __init__(self, source, translations, systems, reference=None, attributes={}, rank_name = u"rank"):
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
        self.tgt = sorted(translations)
        self.systems = systems
        self.ref = reference
        self.attributes = deepcopy(attributes)
        self.rank_name = rank_name
        self._normalize_ranks()
#        self.ties_allowed = ties_allowed

        
    def _normalize_ranks(self):
        """
        Receives two rank scores for the two respective system outputs, compares them and returns a universal
        comparison value, namely -1 if the first system is better, +1 if the second system output is better, 
        and 0 if they are equally good. 
        """
        rank_a = self.tgt[0].get_attribute(self.rank_name)
        rank_b = self.tgt[1].get_attribute(self.rank_name)
        
        if rank_a > rank_b:
            rank = 1
        elif rank_b > rank_a:
            rank = -1
        else:
            rank = 0
        self.attributes[self.rank_name] = str(rank)
#        del(self.tgt[0].attributes[self.rank_name])
#        del(self.tgt[1].attributes[self.rank_name])
        
    def get_system_names(self):
        return self.systems
    
    def get_rank(self):
        return self.attributes[self.rank_name]
    
    def get_translations(self):
        return self.tgt
    
    def get_reversed(self):
        new_attributes = deepcopy(self.attributes)
        new_attributes[self.rank_name] = -1 * new_attributes[self.rank_name]
        return PairwiseParallelSentence(self.src, (self.tgt[1], self.tgt[0]), (self.systems[1], self.systems[0]), self.ref )
