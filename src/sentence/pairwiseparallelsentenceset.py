#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 12, 2011

@author: jogin
'''

class PairwiseParallelSentenceSet():
    
    def __init__(self, pps_list):
        """
        @param pps_list: a list of pairwise parallel sentences
        @type pps_list: a list of PairwiseParallelSentence() objects
        """
        self.pps_list = pps_list
        self.pps_dict = {}
        for pps in pps_list:
            self.pps_dict[pps.get_system_names()] = pps
    
    def get_pairwise_parallelsentence(self, system_names):
        """
        @param system_names: names of translation systems
        @type system_names: tuple of strings
        @return:  
        @return type: PairwiseParallelSentence object
        """
        return self.pps_dict[system_names]
