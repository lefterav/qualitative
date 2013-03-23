'''
This module allows for the calculation of the basic rank metrics that evaluate
on a segment level (i.e. one ranking list at a time)

Created on 18 Dec 2012

@author: Eleftherios Avramidis
'''

from collections import namedtuple
import segment
from numpy import average

import numpy as np

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
      - average segment Kendall tau score,
      - the probability for the null hypothesis of X and Y being independent
      - the count of concordant pairs,
      - the count of discordant pairs,
      - the count of pairs used for calculating tau (excluding "invalid" pairs)
      - the count of original ties,
      - the count of predicted ties,
      - the count of all pairs
    @rtype: dict(float, float, int, int, int, int, int, int)
    
    """
    segtaus = []
    segprobs = []
    
    concordant = 0
    discordant = 0
    valid_pairs = 0
    original_ties_overall = 0
    predicted_ties_overall = 0
    pairs_overall = 0
    sentences_with_ties = 0
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        
        
        segtau, segprob, concordant_count, discordant_count, all_pairs_count, original_ties, predicted_ties, pairs = segment.kendall_tau(predicted_rank_vector, original_rank_vector, **kwargs)
        
        if segtau and segprob:
            segtaus.append(segtau)
            segprobs.append(segprob)
            
        concordant += concordant_count
        discordant += discordant_count
        valid_pairs += all_pairs_count
        
        original_ties_overall += original_ties
        predicted_ties_overall += predicted_ties
        if predicted_ties > 0:
            sentences_with_ties += 1
        pairs_overall += pairs
    
    
    tau = 1.00 * (concordant - discordant) / (concordant + discordant)
    prob = segment.kendall_tau_prob(tau, valid_pairs)
    
    avg_seg_tau = np.average(segtaus)               
    avg_seg_prob = np.product(segprobs)
    
    predicted_ties_avg = 100.00*predicted_ties / pairs_overall
    sentence_ties_avg = 100.00*sentences_with_ties / len(predicted_rank_vector)
    
    stats = {'tau': tau,
             'prob': prob,
             'avg_seg_tau': avg_seg_tau,
             'avg_seg_prob': avg_seg_prob,
             'concordant': concordant,
             'discordant': discordant,
             'valid_pairs': valid_pairs,
             'all_pairs': pairs_overall,
             'original_ties': original_ties_overall,
             'predicted_ties': predicted_ties_overall,
             'predicted_ties_per': predicted_ties_avg,
             'sentence_ties': sentences_with_ties,
             'sentence_ties_per' : sentence_ties_avg
             
             }

    return stats


def mrr(predicted_rank_vectors, original_rank_vectors, **kwargs):

    reciprocal_ranks = []
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        reciprocal_rank = segment.reciprocal_rank(predicted_rank_vector, original_rank_vector)        
        reciprocal_ranks.append(reciprocal_rank)
                
    return {'mrr' : average(reciprocal_ranks)}


def best_predicted_vs_human(predicted_rank_vectors, original_rank_vectors):
    actual_values_of_best_predicted = {}
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        if not predicted_rank_vector:
                continue
        best_predicted_rank = min(predicted_rank_vector)
        original_rank_order = sorted(original_rank_vector)
        
        
            
        original_ranks = []
        for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
            if predicted_rank == best_predicted_rank:
                corrected_original_rank = original_rank_order.index(original_rank) + 1
                original_ranks.append(corrected_original_rank)
                
            
        selected_original_rank = max(original_ranks)
        a = actual_values_of_best_predicted.setdefault(selected_original_rank, 0)
        actual_values_of_best_predicted[selected_original_rank] = a + 1

    n = len(predicted_rank_vectors)
    percentages = {}
    total = 0
    for rank, counts in  actual_values_of_best_predicted.iteritems():
        percentages["bph_" + str(rank)] = round(100.00 * counts / n , 2 )
        total += counts
    return percentages


def avg_ndgc_err(predicted_rank_vectors, original_rank_vectors, **kwargs):
    ndgc_list = []
    err_list = []
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        k = kwargs.setdefault('k', len(predicted_rank_vector))
        ndgc, err = segment.ndgc_err(predicted_rank_vector, original_rank_vector, k)
        ndgc_list.append(ndgc)
        err_list.append(err)
    avg_ndgc = average(ndgc)
    avg_err = average(err)
    return {'ndgc':avg_ndgc, 'err':avg_err}
    