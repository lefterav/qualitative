#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin, elav01
'''
from pairwiseparallelsentence import PairwiseParallelSentence
from copy import deepcopy
from parallelsentence import ParallelSentence
import logging
from collections import OrderedDict

    

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
    

    def length(self):
        return len(self.get_parallelsentences())    
    

class AnalyticPairwiseParallelSentenceSet(PairwiseParallelSentenceSet):
    """
    A set of pairwise parallel sentences, all originating from the same source sentence, where more than one comparisons per system-pair are allowed
    @ivar pps_dict: a dict that stores all the pairwise parallelsentences mapped to a tuple of strings containing the system names for the respective translations 
    @type pps_dict: {(str, str): [L{PairwiseParallelSentence}, ...]} 
    """
    def __init__(self, pairwise_parallelsentences = [], rank_name = "rank", **kwargs):
        """
        @param pairwise_parallelsentences: a list of pairwise parallel sentences
        @type pairwise_parallelsentences: [L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}, ...]
        """
        self.pps_dict = OrderedDict()
        self.rank_name = kwargs.setdefault("rank_name", rank_name)
        
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
        """
        It removes the pairwise sentences whose rank is equal with each other's
        @return: the number of ties filtered
        @rtype: int
        @todo: test
        """
        reformed_dict = OrderedDict()
        removed_ties = 0  
        for system_names in self.pps_dict:
            reformed_dict[system_names] = [ps for ps in self.pps_dict[system_names] if int(ps.get_attribute(self.rank_name)) != 0]
            removed_ties += len(self.pps_dict[system_names]) - len(reformed_dict[system_names])
        
        self.pps_dict = reformed_dict
        return removed_ties
    
    
    def restrict_ranks(self, restrict_ranks):
        pass
        restrict_ranks = set([float(r) for r in restrict_ranks])
        print
        print restrict_ranks
        for system_names in self.pps_dict.keys():
            ps_restricted = []
            for ps in self.pps_dict[system_names]:
                target_ranks = set([float(r) for r in ps.get_target_attribute_values(self.rank_name)])
                print target_ranks,
                if not target_ranks.isdisjoint(restrict_ranks):
                    ps_restricted.append(ps)
                    print "ok"
                else:
                    print 
            if ps_restricted:
                self.pps_dict[system_names] = ps_restricted
            else:
                del self.pps_dict[system_names]
                                
            

    
    def get_pairwise_parallelsentences(self, system_names, directed = False):
        """
        Provides the pairwise parallel sentences, whose target sentences provide output by the two given systems
        @param system_names: pair of translation system names
        @type system_names: tuple of strings
        @param order: whether the order of the systems in the tuple is important, or not
        @type order: boolean
        @return: the pairwise parallel sentence that contains the outputs of the two given systems
        @rtype: [L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}, ...]
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
    
    
    def get_filtered_pairwise_parallelsentence_set(self, threshold = 1.00):
        return CompactPairwiseParallelSentenceSet(self.get_filtered_pairwise_parallelsentences(threshold))
    
    
    def get_filtered_pairwise_parallelsentences(self, threshold = 1.00):
        filtered_pairwise_parallelsentences = []
        for system_names in self.get_system_names():
            overlapping_judgments = self.get_pairwise_parallelsentences(system_names)
            filtered_pairwise_parallelsentence = self._filter_agreement(threshold, overlapping_judgments, system_names)
            if filtered_pairwise_parallelsentence:
                filtered_pairwise_parallelsentences.append(filtered_pairwise_parallelsentence)
        return filtered_pairwise_parallelsentences
    
    def _filter_agreement(self, threshold = 1.00, pairwise_parallelsentences = [], system_names=()):
        if len(pairwise_parallelsentences) == 1:
            return pairwise_parallelsentences[0]
        rank_vector = [ps.get_rank() for ps in pairwise_parallelsentences]
        rank_values = set(rank_vector)
        rank_distribution = sorted([(rank_vector.count(rank)*1.00/len(rank_vector), rank) for rank in rank_values])
        most_popular = rank_distribution[-1]
        if most_popular[0] >= threshold:
            #return the first pairwise sentence that appears to have this rank
            for ps in pairwise_parallelsentences:
                if ps.get_rank() == most_popular[1]:
                    return ps 
        else:
            return None
             
    
    def get_compact_pairwise_parallelsentences(self):
        return self.get_merged_pairwise_parallelsentences()
    
    def get_merged_pairwise_parallelsentences(self):
        """
        Merge many overlapping judgments over translations originating from the same source sentence
        @return pairwise parallel sentences, containing only the merged output rank
        @rtype [L{L{sentence.pairwiseparallelsentence.PairwiseParallelSentence}, ...] 
        """
        merged_pairwise_parallelsentences = []
        for system_names in self.get_system_names():
            overlapping_judgments = self.get_pairwise_parallelsentences(system_names)
            merged_pairwise_parallelsentence = self._merge_judgments(overlapping_judgments, system_names)
            merged_pairwise_parallelsentences.append(merged_pairwise_parallelsentence)
        return merged_pairwise_parallelsentences
    
    def get_compact_pairwise_parallelsentence_set(self):
        return CompactPairwiseParallelSentenceSet(self.get_compact_pairwise_parallelsentences())
        
    def _merge_judgments(self, pairwise_parallelsentences = [], system_names=()):
        """
        Merge many overlapping judgements over translations produced by the same system pair
        originating from the same source sentence, into only one judgment
        @return: a pairwise parallel sentences
        @rtype: L{PairwiseParallelSentence}
        """        
        rank = sum([float(ps.get_rank()) * self._merge_weight(ps) for ps in pairwise_parallelsentences])
        
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
    A compact set of pairwise parallel sentences, all originating from the same source sentence,
    where only one comparison per system-pair is allowed
    @ivar rank_name: the name of the rank value
    @type rank_name: str
    @ivar pps_dict: a dictionary of pairwise parallelel sentences
    @type pps_dict: {(str, str): L{PairwiseParallelSentence}} 
    """
    
    def __init__(self, pairwise_parallelsentences, rank_name = "rank"):
        """
        @param pairwise_parallelsentences: a list of pairwise parallel sentences
        @type pairwise_parallelsentences: [L{PairwiseParallelSentence}, ...]
        """
        self.rank_name = rank_name
        self.pps_dict = dict([(ps.get_system_names(), ps) for ps in pairwise_parallelsentences])
        pass
    
    
    def remove_ties(self):
        """
        It removes the pairwise sentences whose rank is equal with each other's
        @return: the number of ties filtered
        @rtype: int
        """
        reformed_dict = OrderedDict()
        ties = 0
        for system_names in self.pps_dict:
            ps = self.pps_dict[system_names]
            if int(ps.get_attribute(self.rank_name)) != 0:
                reformed_dict[system_names] = ps
            else:
                ties += 1
        self.pps_dict = reformed_dict       
        
        print "filtered %d ties" % ties
        return ties
    
    def get_multiranked_sentence(self, critical_attribute = None, new_rank_name = None, del_orig_class_att = True):
        """
        It reconstructs a single parallel sentence object with a gathered discrete [1-9] 
        ranking out of the pairwise comparisons that exist in the pairwise parallel sentence instances
        @return: a parallel sentence
        @rtype: L{ParallelSentence} 
        """
        rank_per_system = OrderedDict()
        translations_per_system = OrderedDict()
        
        if not new_rank_name:
            new_rank_name = self.rank_name
        

        
        #first iterate and make a sum of the rank per system name        
        for (system_a, system_b), parallelsentence in self.pps_dict.iteritems():
            #get the rank value (0, -1, 1)
                        
            if not critical_attribute:
                rank = int(parallelsentence.get_rank())
            else:
                rank = int(parallelsentence.get_attribute(critical_attribute))
            
            #rank value adds up on the first system's rank
            #and subtracts from the seconds system's

            rank_per_system[system_a] = rank_per_system.setdefault(system_a, 0) + rank
            #rank_per_system[system_b] = rank_per_system.setdefault(system_b, 0) - rank
            
            #also gather in a dict the translations per system name, in order to have easy access later
            translations_per_system[system_b] = parallelsentence.get_translations()[1]
            translations_per_system[system_a] = parallelsentence.get_translations()[0]

        
        #normalize ranks
        i = 0
        prev_rank = None
        translations_new_rank = [] #list that gathers all the translations
                
        #iterate through the system outputs, sorted by their rank
        #and increment their rank only if there is no tie
        systems = sorted(rank_per_system, key=lambda system: rank_per_system[system])
        for system in systems:
            #if there is no tie                
            if rank_per_system[system] != prev_rank: 
                i += 1
                    
            #print "system: %s\t%d -> %d" % (system, rank_per_system[system] , i)
#                print i, system,
            prev_rank = rank_per_system[system]
            translation = deepcopy(translations_per_system[system])
            translation.add_attribute(new_rank_name, str(i))
            translations_new_rank.append(translation)
        
        #get the values of the first sentence as template
        source = deepcopy(self.pps_dict.values()[0].get_source())
        reference = deepcopy(self.pps_dict.values()[0].get_reference())
        attributes = deepcopy(self.pps_dict.values()[0].get_attributes())
#        if del_orig_class_att:
#            del(attributes[self.rank_name])
        try:
        	del(attributes[self.rank_name])
        except:
             pass
        
        return ParallelSentence(source, translations_new_rank, reference, attributes)         
        

    def get_multiranked_sentence_with_probfilter(self, attribute1="", attribute2="", critical_attribute="rank_soft_predicted", new_rank_name = None, threshold=0.1000):
        """
        It reconstructs a single parallel sentence object with a gathered discrete [1-9] 
        ranking out of the pairwise comparisons that exist in the pairwise parallel sentence instances
        @return: a parallel sentence
        @rtype: L{ParallelSentence} 
        """
        rank_per_system = OrderedDict()
        translations_per_system = OrderedDict()
        
        if not new_rank_name:
            new_rank_name = self.rank_name
        
        fullrank = False
                
        while not fullrank:
            #first iterate and make a sum of the rank per system name        
            for (system_a, system_b), parallelsentence in self.pps_dict.iteritems():
                logging.debug("threshold: {}".format(threshold))
                
                #get the rank probability                
                prob_neg = float(parallelsentence.get_attribute(attribute1))
                
                #rank value adds up on the first system's rank
                #only if it is "sure" enough
                if abs(prob_neg-0.5) > threshold:
                    try:
                        rank_per_system[system_b] += prob_neg
                    except KeyError:
                        rank_per_system[system_b] = prob_neg
    #            also gather in a dict the translations per system name, in order to have easy access later
                translations_per_system[system_b] = parallelsentence.get_translations()[1]
                translations_per_system[system_a] = parallelsentence.get_translations()[0]
            
                
                fullrank = True
                for system_a, system_b in self.get_system_names():
                    if system_b not in rank_per_system:
                        logging.debug("didn't fill in one rank")
                        fullrank = False
                        threshold = threshold - threshold/20
                        break
                    
                #run one last time with threshold 1
                if threshold < 0.002:
                    threshold = 0
                if threshold == 0:
                    fullrank = True
            
        #normalize ranks
        i = 0
        prev_rank = None
        translations_new_rank = [] #list that gathers all the translations
                
        #iterate through the system outputs, sorted by their rank
        #and increment their rank only if there is no tie
        systems = sorted(rank_per_system, key=lambda system: rank_per_system[system])
        print systems
        for system in systems:
            #if there is no tie                
            if rank_per_system[system] != prev_rank: 
                i += 1
                    
            #print "system: %s\t%d -> %d" % (system, rank_per_system[system] , i)
#                print i, system,
            prev_rank = rank_per_system[system]
            translation = deepcopy(translations_per_system[system])
            translation.add_attribute(new_rank_name, str(i))
            translations_new_rank.append(translation)
        
        #get the values of the first sentence as template
        source = deepcopy(self.pps_dict.values()[0].get_source())
        reference = deepcopy(self.pps_dict.values()[0].get_reference())
        attributes = deepcopy(self.pps_dict.values()[0].get_attributes())
        try:
            del(attributes[new_rank_name])
        except:
            pass
        
        return ParallelSentence(source, translations_new_rank, reference, attributes)      

    def get_multiranked_sentence_with_soft_ranks(self, attribute1="", attribute2="", critical_attribute="rank_soft_predicted", new_rank_name = None):
        """
        It reconstructs a single parallel sentence object with a gathered discrete [1-9] 
        ranking out of the pairwise comparisons that exist in the pairwise parallel sentence instances
        @return: a parallel sentence
        @rtype: L{ParallelSentence} 
        """
        rank_per_system = OrderedDict()
        translations_per_system = OrderedDict()
        
        if not new_rank_name:
            new_rank_name = self.rank_name
        
        #first iterate and make a sum of the rank per system name        
        for (system_a, system_b), parallelsentence in self.pps_dict.iteritems():
            #get the rank value (0, -1, 1)
            
            prob_neg = float(parallelsentence.get_attribute(attribute1))
#            prob_pos = -1.00 * float(parallelsentence.get_attribute(attribute2))
            
            
            #rank value adds up on the first system's rank
            #and subtracts from the seconds system's -> found out that this doesn't help
            try:
                rank_per_system[system_b] += prob_neg
            except KeyError:
                rank_per_system[system_b] = prob_neg
#            try:
#                rank_per_system[system_a] -= prob_pos
#            except KeyError:
#                rank_per_system[system_a] = -1 * prob_pos
#            
            #also gather in a dict the translations per system name, in order to have easy access later
            translations_per_system[system_b] = parallelsentence.get_translations()[1]
            translations_per_system[system_a] = parallelsentence.get_translations()[0]

        
        #normalize ranks
        i = 0
        prev_rank = None
        translations_new_rank = [] #list that gathers all the translations
                
        #iterate through the system outputs, sorted by their rank
        #and increment their rank only if there is no tie
        systems = sorted(rank_per_system, key=lambda system: rank_per_system[system])
        print systems
        for system in systems:
            #if there is no tie                
            if rank_per_system[system] != prev_rank: 
                i += 1
                    
            #print "system: %s\t%d -> %d" % (system, rank_per_system[system] , i)
#                print i, system,
            prev_rank = rank_per_system[system]
            translation = deepcopy(translations_per_system[system])
            translation.add_attribute(new_rank_name, str(i))
            translations_new_rank.append(translation)
        
        #get the values of the first sentence as template
        source = deepcopy(self.pps_dict.values()[0].get_source())
        reference = deepcopy(self.pps_dict.values()[0].get_reference())
        attributes = deepcopy(self.pps_dict.values()[0].get_attributes())
        try:
            del(attributes[new_rank_name])
        except:
            pass
        
        return ParallelSentence(source, translations_new_rank, reference, attributes)         


    
    def get_pairwise_parallelsentence(self, system_names, directed = False):
        """
        Provides the pairwise parallel sentence, whose target sentences provide output by the two given systems
        @param system_names: pair of translation system names
        @type system_names: tuple of strings
        @param order: whether the order of the systems in the tuple is important, or not
        @type order: boolean
        @return: the pairwise parallel sentence that contains the outputs of the two given systems
        @rtype: L{PairwiseParallelSentence}
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


