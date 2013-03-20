'''
Created on 18 Dec 2012

@author: Eleftherios Avramidis
'''

from collections import namedtuple
import segment

def kendall_tau(predicted_rank_vectors, original_rank_vectors, **kwargs):
    """
    This is the refined calculation of set-level Kendall tau of predicted vs human ranking according to WMT12 (Birch et. al 2012)
    It returns both set-level Kendall tau and average segment-level Kendall tau
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [[str, ..], ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank, one ranking for each segment
    @type original_rank_vectors: [[str, ..], ..] 
    @kwarg invert_ranks: set to True, if you need the coefficient to be calculated on the inverted rank. Defaults to False
    @type invert_ranks: boolean 
    @return: overall Kendall tau score,
     average segment Kendall tau score,
     the probability for the null hypothesis of X and Y being independent
     the count of concordant pairs,
     the count of discordant pairs,
     the count of pairs used for calculating tau (excluding "invalid" pairs)
     the count of original ties,
     the count of predicted ties,
     the count of all pairs
    @rtype: tuple(float, float, int, int, int, int, int, int)
    
    """
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        seg = segment.kendall_tau(predicted_rank_vector, original_rank_vector) 
        