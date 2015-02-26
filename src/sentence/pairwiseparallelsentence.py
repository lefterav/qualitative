#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: Lukas Poustka
'''


from parallelsentence import ParallelSentence 
from copy import deepcopy



class PairwiseParallelSentence(ParallelSentence):
    """
    A pairwise parallel sentence, is a parallel sentence that contains output produced by only two systems.
    @ivar src: the source sentence
    @type src: SimpleSentence
    @ivar translations: a tuple of two target sentences
    @type translations: tuple(Simplesentence, SimpleSentence)
    @ival reference: the reference translation
    @type reference: L{SimpleSentence}
    @ival attributes: a dict with the attributes at the parallel sentence level
    @type attributes: dict{str : str}
    @ivar rank_name: the name of the attribute that serves as the rank
    @type rank_name: str   
    """

    def __init__(self, source=None, translations=[], systems=[], reference=None, attributes={}, rank_name = u"rank", normalize_ranks=True, **kwargs):
        """
        Constructor
        @param source: the source text of the parallel sentence
        @type source: SimpleSentence
        @param translations: a pair of translations
        @type translations: tuple of translations (SimpleSentence, SimpleSentence)
        @param reference: The desired translation provided by the system
        @type reference: SimpleSentence 
        @param the attributes: that describe the parallel sentence
        @type attributes: dict { String name : String value }
        @param systems: names of target systems
        @type systems: tuple of strings
        @param cast: set True if you want to initialize a pairwise parallel sentence out of a simple parallel sentence
        """
        
        cast = kwargs.setdefault("cast", None)
        rankless = kwargs.setdefault("rankless",False)
        invert_ranks = kwargs.setdefault("invert_ranks", False)
        
        
        if cast:
            self._cast(cast)
        else:
            self.src = source 
            self.tgt = translations
            self.systems = systems
            self.ref = reference
            self.attributes = deepcopy(attributes)
            self.rank_name = rank_name
            if self.tgt and normalize_ranks and not rankless and rank_name:
                self._normalize_ranks(invert_ranks)
    #        self.ties_allowed = ties_allowed

    def _cast(self, parallelsentence):
        """
        Reload in place a pairwise parallelsentence which has the type of a simple parallelsentence
        @param parellesenentence: the simple parallelsentence
        @type parallelsentence: L{ParallelSentence}
        """
        self.src = parallelsentence.src
        self.tgt = parallelsentence.tgt
        self.systems = tuple([tgt.get_attribute("system") for tgt in self.tgt])
        self.ref = parallelsentence.ref
        self.attributes = parallelsentence.attributes
        self.rank_name = parallelsentence.rank_name
        
    
    def _normalize_ranks(self, invert_ranks=False):
        """
        Reads the two rank scores for the two respective system outputs, compares them and sets a universal
        comparison value, namely -1 if the first system is better, +1 if the second system output is better, 
        and 0 if they are equally good. The value is set as a new argument of the current object
        @param invert_ranks: If set to True, it inverts the ranks (useful for non-penalty metrics)
        @type invert_ranks: boolean
        """
        
        if invert_ranks:
            factor = -1.00
        else:
            factor = 1.00 
        
        try:
            rank_a = float(self.tgt[0].get_attribute(self.rank_name)) * factor
            rank_b = float(self.tgt[1].get_attribute(self.rank_name)) * factor
        except KeyError:
            #this happens if for some reasons no rank values have been written
            #in that case normalization does not make sense
            return
        
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
