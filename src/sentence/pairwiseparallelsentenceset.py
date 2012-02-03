#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin
'''
from pairwiseparallelsentence import PairwiseParallelSentence
from copy import deepcopy

class PairwiseParallelSentenceSet():
    """
    A set of pairwise parallel sentences, all originating from the same source sentence, in order to facilitate pairwise comparisons etc. 
    Works as a wrapper over a dictionary, where pairs are indexed based on the system names of the 2 target translations.
    """
    def get_parallelsentences(self):
        """
        @return: a list of the parallel sentences contained in the structure
        @rtype: pairwise_parallelsentences: list of L{sentence.pairwiseparallelsentence.PairwiseParallelSentence} instances
        """
        return self.pps_dict.values()
    
    def get_system_names(self):
        """
        @return: all the system pairs that are mapped to pairwise sentences
        @rtype: list of tuples of two strings each
        """
        return self.pps_dict.keys()
    

class AnalyticPairwiseParallelSentenceSet(PairwiseParallelSentenceSet):
    """
    A set of pairwise parallel sentences, all originating from the same source sentence, where more than one comparisons per system-pair are allowed
    """
    def __init__(self, pairwise_parallelsentences = [], rank_name = "rank"):
        """
        @param pairwise_parallelsentences: a list of pairwise parallel sentences
        @type pairwise_parallelsentences: list of L{sentence.pairwiseparallelsentence.PairwiseParallelSentence} instances
        """
        self.pps_dict = {}
        self.rank_name = rank_name
        for ps in pairwise_parallelsentences:
            system_names = ps.get_system_names()
            try:
                self.pps_dict[system_names].append(ps)
            except KeyError:
                self.pps_dict[system_names] = [ps]
    
    def get_parallelsentences(self):
        all_parallelsentences = []
        for parallelsentencelist in self.pps_dict.values():
            all_parallelsentences.extend(parallelsentencelist)
        return all_parallelsentences
                
            
    def remove_ties(self):
        reformed_dict = {}
        for system_names in self.pps_dict:
            reformed_dict[system_names] = [ps for ps in self.pps_dict[system_names] if int(ps.get_attribute(self.rank_name)) != 0]
        self.pps_dict = reformed_dict
    
    
    def get_pairwise_parallelsentences(self, system_names, directed = False):
        """
        Provides the pairwise parallel sentences, whose target sentences provide output by the two given systems
        @param system_names: pair of translation system names
        @type system_names: tuple of strings
        @param order: whether the order of the systems in the tuple is important, or not
        @type order: boolean
        @return: the pairwise parallel sentence that contains the outputs of the two given systems
        @rtype: list of L{L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}} instances
        """
        try:
            return self.pps_dict[system_names]
        except:
            if not directed:
                try:
                    system_names_reversed = (system_names[1], system_names[0])
                    return self.pps_dict[system_names_reversed].get_reversed()
                except:
                    print "At least one of system names is missing."
            else:
                print "At least one of system names is missing."
    
    def get_compact_pairwise_parallelsentences(self):
        """
        Merge many overlapping judgments over translations originating from the same source sentence
        @return pairwise parallel sentences, containing only the merged output rank
        @rtype list of L{L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}.PairwiseParallelSentence} instances 
        """
        merged_pairwise_parallelsentences = []
        for system_names in self.get_system_names():
            overlapping_judgments = self.get_pairwise_parallelsentences(system_names)
            merged_pairwise_parallelsentence = self.merge_judgments(overlapping_judgments, system_names)
            merged_pairwise_parallelsentences.append(merged_pairwise_parallelsentence)
        return merged_pairwise_parallelsentences
    
    def get_compact_pairwise_parallelsentence_set(self):
        return CompactPairwiseParallelSentenceSet(self.get_compact_pairwise_parallelsentences())
        
    def merge_judgments(self, pairwise_parallelsentences = [], system_names=()):
        """
        Merge many overlapping judgements over translations produced by the same system pair
        originating from the same source sentence, into only one judgment
        """
        rank = 0
        for ps in pairwise_parallelsentences:
            rank += ps.get_rank() * self._merge_weight(ps)
        
        attributes = deepcopy(pairwise_parallelsentences[0].attributes)
        attributes[self.rank_name] = rank
        source = pairwise_parallelsentences[0].get_source()
        translations = pairwise_parallelsentences[0].get_translations()
        reference = pairwise_parallelsentences[0].get_reference()
        new_ps = PairwiseParallelSentence(source, translations, system_names, reference, attributes, self.rank_name)
        return new_ps
    
    def _merge_weight(self, ps):
        return 1
            
        
        
        

class CompactPairwiseParallelSentenceSet(PairwiseParallelSentenceSet):
    """
    A compact set of pairwise parallel sentences, all originating from the same source sentence, where only one comparison per system-pair is allowed 
    """
    
    def __init__(self, pairwise_parallelsentences = [], rank_name = "rank"):
        """
        @param pairwise_parallelsentences: a list of pairwise parallel sentences
        @type pairwise_parallelsentences: list of L{sentence.pairwiseparallelsentence.PairwiseParallelSentence} instances
        """
        self.rank_name = rank_name
        self.pps_dict = dict([(ps.get_system_names(), ps) for ps in pairwise_parallelsentences])
    
    
    def remove_ties(self):
        for system_names in self.pps_dict:
            if int(self.pps_dict[system_names].get_attribute(self.rank_name)) == 0:
                del(self.pps_dict[system_names])
    
    def get_pairwise_parallelsentence(self, system_names, directed = False):
        """
        Provides the pairwise parallel sentence, whose target sentences provide output by the two given systems
        @param system_names: pair of translation system names
        @type system_names: tuple of strings
        @param order: whether the order of the systems in the tuple is important, or not
        @type order: boolean
        @return: the pairwise parallel sentence that contains the outputs of the two given systems
        @rtype: L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}
        """
            
        try:
            return self.pps_dict[system_names]
        except:
            if not directed:
                try:
                    system_names_reversed = (system_names[1], system_names[0])
                    return self.pps_dict[system_names_reversed]
                except:
                    print "At least one of system names is missing."
            else:
                print "At least one of system names is missing."
