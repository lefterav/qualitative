#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""

from dataset import DataSet
from scipy.stats import spearmanr

class Spearman(DataSet):
    """
    classdocs
    """
    
    
    def get_spearman_correlation(self):
        original_ranks = []
        estimated_ranks = []
        for parallelsentence in self.parallelsentences:
            sample_original_ranks = []
            sample_estimated_ranks = []
            for target in parallelsentence.get_translations():
                sample_original_ranks.append(parallelsentence.get_attribute("orig_rank"))
                sample_estimated_ranks.append(parallelsentence.get_attribute("rank"))
            original_ranks.append
        
        return spearmanr()
        
        
    
        
        