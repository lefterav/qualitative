#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin
'''

class PairwiseParallelSentenceSet():
    """
    A set of pairwise parallel sentences, in order to facilitate pairwise comparisons etc. 
    Works as a wrapper over a dictionary, where pairs are indexed based on the system names of the 2 target translations.
    """
    
    def __init__(self, pps_list):
        """
        @param pps_list: a list of pairwise parallel sentences
        @type pps_list: a list of PairwiseParallelSentence() objects
        """
        self.pps_list = pps_list
        self.pps_dict = {}
        for pps in pps_list:
            self.pps_dict[pps.get_system_names()] = pps
    
    def get_pairwise_parallelsentence(self, system_names, order = True):
        """
        Provides the pairwise parallel sentence, whose target sentences provide output by the two given systems
        @param system_names: pair of translation system names
        @type system_names: tuple of strings
        @param order: whether the order of the systems in the tuple is important, or not
        @type order: boolean
        @return: the pairwise parallel sentence that contains the outputs of the two given systems
        @return type: PairwiseParallelSentence object
        """
            
        try:
            return self.pps_dict[system_names]
        except:
            if not order:
                try:
                    system_names_reversed = (system_names[1], system_names[0])
                    return self.pps_dict[system_names_reversed]
                except:
                    print "At least one of system names is missing."
            else:
                print "At least one of system names is missing."
