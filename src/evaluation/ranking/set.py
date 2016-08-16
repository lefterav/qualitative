'''
This module allows for the calculation of the basic rank_strings metrics that evaluate
on a segment level (i.e. one ranking list at a time)

Created on 18 Dec 2012

@author: Eleftherios Avramidis
'''

import segment
from numpy import average
import numpy as np
import logging
from collections import OrderedDict, defaultdict
from scipy.special import erfc

def kendall_tau_set_no_ties(predicted_rank_vectors, original_rank_vectors, **kwargs):
    kwargs["penalize_predicted_ties"] = False
    result = kendall_tau_set(predicted_rank_vectors, original_rank_vectors, **kwargs)
    newresult = {}
    for key, value in result.iteritems():
        newkey = key.replace("tau", "tau-nt")
        newresult[newkey] = value
    return newresult    

def kendall_tau_set(predicted_rank_vectors, original_rank_vectors, **kwargs):
    """
    This is the refined calculation of set-level Kendall tau of predicted vs human ranking according to WMT12 (Birch et. al 2012)
    It returns both set-level Kendall tau and average segment-level Kendall tau
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [Ranking, ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank_strings, one ranking for each segment
    @type original_rank_vectors: [Ranking, ..] 
    @return: overall Kendall tau score,
      - average segment Kendall tau score,
      - the probability for the null hypothesis of X and Y being independent
      - the count of concordant pairs,
      - the count of discordant pairs,
      - the count of pairs used for calculating tau (excluding "invalid" pairs)
      - the count of original ties,
      - the count of predicted ties,
      - the count of all pairs
    @rtype: {string:float, string:float, string:int, string:int, string:int, string:int, string:int, string:int}
    
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

    #count how many ranking lists exist for each length (e.g 100 lists with length 5 etc.)
    ranking_counts_per_length = defaultdict(int)   
    sum_tau_per_length = defaultdict(float)
    #sums for the fractions of the 
    sum_inverted_single_max_variance = 0
    sum_weighed_variance = 0
    sum_ranking_lengths = 0
    skipped = 0
    count = 0
    non_significant_count = 0
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        
        segtau, segprob, concordant_count, discordant_count, all_pairs_count, original_ties, predicted_ties, pairs = segment.kendall_tau(predicted_rank_vector, original_rank_vector, **kwargs)
        ranking_length = len(predicted_rank_vector)
        
        if segtau == None:
            logging.debug("Segment tau was found to be {}".format(segtau))
            # and segprob):
            skipped += 1
        else:
            count += 1                    
            segtaus.append(segtau)
            segprobs.append(segprob)
            
            if segprob >= 0.05:
                non_significant_count += 1
                
            #gather statistics per length to calculate significance for null hypothesis
            ranking_counts_per_length[ranking_length] += 1
            sum_tau_per_length[ranking_length] += segtau
            
            #maximum variance
            max_var = (1.00 - segtau*segtau) / (ranking_length / 2.00)
            #sum of item variance weighed by ranking length, used for the nominator of the pooled variance
            sum_weighed_variance += (ranking_length - 1) * max_var
            #sum of inverted maximum variance used for the denominator weighed standard error (4.9)
            try:
                sum_inverted_single_max_variance += 1.00 / max_var
            except ZeroDivisionError:
                sum_inverted_single_max_variance += 1.00 / 0.0000000001
            #sum of ranking length
            sum_ranking_lengths += ranking_length - 1
            
        #sum overal pair identities            
        concordant += concordant_count
        discordant += discordant_count
        valid_pairs += all_pairs_count
        
        original_ties_overall += original_ties
        predicted_ties_overall += predicted_ties
        if predicted_ties > 0:
            sentences_with_ties += 1
        pairs_overall += pairs
    
    if skipped:
        logging.warn("{} items were skipped from tau calculation".format(skipped))
    
    #this is probably when the test has only has ties
    if (concordant + discordant) == 0:
        logging.warn("I had to skip item in tau evaluation because of zero pairs")
        return {}
    tau = 1.00 * (concordant - discordant) / (concordant + discordant)
    prob = segment.kendall_tau_prob(tau, valid_pairs)
    
    #average tau statistics
    avg_seg_tau = np.average(segtaus)               
    avg_seg_prob = np.product(segprobs)
    
    non_significant_ratio = (1.00 * non_significant_count) / count
    
    #weighed tau and significance for null hypothesis
    weighed_tau, weighed_prob, variance_per_length = _inverse_weighted_tau(ranking_counts_per_length, sum_tau_per_length)
    
    #maximum standard deviation from the pooled variance
    pooled_std = 1.96 * np.sqrt(sum_weighed_variance / sum_ranking_lengths)
    
    #maximum standard deviation from the mean based on inverse weighed variance
    inverse_weighed_std = 1.96 * np.sqrt(1.00 / sum_inverted_single_max_variance) 
    
    #averages for the ties
    predicted_ties_avg = 100.00*predicted_ties / pairs_overall
    sentence_ties_avg = 100.00*sentences_with_ties / len(predicted_rank_vector)
    
    stats = OrderedDict({'tau': tau,
             'tau_prob': prob,
             'tau_avg_seg': avg_seg_tau,
             'tau_avg_seg_prob': avg_seg_prob,
             'tau_weighed': weighed_tau,
             'tau_weighed_prob': weighed_prob,
             'tau_invw_std': inverse_weighed_std,
             'tau_pooled_std': pooled_std,
             'tau_nonsig_ratio': non_significant_ratio,
             'tau_concordant': concordant,
             'tau_discordant': discordant,
             'tau_valid_pairs': valid_pairs,
             'tau_all_pairs': pairs_overall,
             'tau_original_ties': original_ties_overall,
             'tau_predicted_ties': predicted_ties_overall,
             'tau_predicted_ties_per': predicted_ties_avg,
             'tau_sentence_ties': sentences_with_ties,
             'tau_sentence_ties_per' : sentence_ties_avg
             })

    for n, counts in ranking_counts_per_length.iteritems():
        stats["tau_rank_length_{}".format(n)] = counts
        stats["tau_weighed_var_{}".format(n)] = variance_per_length[n]

    return stats
    

def _inverse_weighted_tau(ranking_counts_per_length, sum_tau_per_length):
    """
    Calculate the overall tau probability given the tau correlations
    from individual segments. For this, only counts and tau sums per
    ranking length are required
    """
    sum_nominator = 0
    sum_denominator = 0
    inv_variance_sum = 0
    variance_per_length = {}
    #iterate for all lengths, i.e. ranking with three, four, etc
    logging.debug("Sum tau per length: {}".format(sum_tau_per_length))
    for length in sum_tau_per_length.keys():
        if length < 2:
            #definition only holds for m >= 2
            continue
        m = 1.00 * length
        n = 1.00 * ranking_counts_per_length[length]
        avg_tau = sum_tau_per_length[length] / n 
        inv_variance = n * (9 * m * (m - 1)) / (2 * (2 * m + 5))
        sum_nominator += inv_variance * avg_tau
        sum_denominator += inv_variance
        inv_variance_sum += inv_variance 
        variance_per_length[length] = 1.00 / inv_variance
    weighed_tau = sum_nominator / sum_denominator
    weighed_variance = 1.00 / inv_variance_sum
    z = weighed_tau / np.sqrt(weighed_variance)
    prob = erfc(np.abs(z) / 1.4142136)
    return weighed_tau, prob, variance_per_length

def mrr(predicted_rank_vectors, original_rank_vectors, **kwargs):
    """
    Calculation of mean reciprocal rank_strings based on Radev et. all (2002)
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [Ranking, ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank_strings, one ranking for each segment
    @type original_rank_vectors: [Ranking, ..]
    @return: mean reciprocal rank_strings
    @rtype: {string, float} 
    """
    reciprocal_ranks = []
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        reciprocal_rank = segment.reciprocal_rank(predicted_rank_vector, original_rank_vector)        
        reciprocal_ranks.append(reciprocal_rank)
                
    return {'mrr' : average(reciprocal_ranks)}


def best_predicted_vs_human(predicted_rank_vectors, original_rank_vectors):
    """
    For each sentence, the item selected as best by our system, may have been ranked lower by the humans. This 
    statistic counts how many times the item predicted as best has fallen into each of the human ranks.
    This is useful for plotting. 
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [Ranking, ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank_strings, one ranking for each segment
    @type original_rank_vectors: [Ranking, ..]
    @return: a dictionary with percentages for each human rank_strings
    @rtype: {string, float}
    """
    actual_values_of_best_predicted = {}
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        
        #make sure vectors are normalized
        predicted_rank_vector = predicted_rank_vector.normalize()
        original_rank_vector = original_rank_vector.normalize()
        if not predicted_rank_vector:
            continue
        best_predicted_rank = min(predicted_rank_vector)
        
        original_ranks = []
        for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
            if predicted_rank == best_predicted_rank:
                original_ranks.append(original_rank)
        
        #if best rank_strings given to many items, get the worst human rank_strings for it
        selected_original_rank = max(original_ranks)
        a = actual_values_of_best_predicted.setdefault(selected_original_rank, 0)
        actual_values_of_best_predicted[selected_original_rank] = a + 1

    n = len(predicted_rank_vectors)
    percentages = {}
    total = 0
    #gather everything into a dictionary
    for rank_strings, counts in  actual_values_of_best_predicted.iteritems():
        percentages["bph_" + str(rank_strings)] = round(100.00 * counts / n , 2 )
        total += counts
    return percentages

def avg_predicted_ranked(predicted_rank_vectors, original_rank_vectors, **kwargs):
    
    """
    It will provide the average human rank_strings of the item chosen by the system as best
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [Ranking, ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank_strings, one ranking for each segment
    @type original_rank_vectors: [Ranking, ..]
    @return: a dictionary with the name of the metric and its value
    @rtype: {string, float}
    """
    
    original_ranks = []
    
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):        
        
        #make sure vectors are normalized
        predicted_rank_vector = predicted_rank_vector.normalize(ties='ceiling')
        original_rank_vector = original_rank_vector.normalize(ties='ceiling')
        
        best_predicted_rank = min(predicted_rank_vector)
        mapped_original_ranks = []
        
        for original_rank, predicted_rank in zip(original_rank_vector, predicted_rank_vector):
            if predicted_rank == best_predicted_rank:
                mapped_original_ranks.append(original_rank)
        
        #in case of ties get the worst one
        original_ranks.append(max(mapped_original_ranks))
    
    return {'avg_predicted_ranked': average(original_ranks)}
        
        


def avg_ndgc_err(predicted_rank_vectors, original_rank_vectors, **kwargs):
    """
    Returns normalize Discounted Cumulative Gain and the Expected Reciprocal Rank, both averaged over number of sentences
    @param predicted_rank_vectors: a list of lists containing integers representing the predicted ranks, one ranking for each segment
    @type predicted_rank_vectors: [Ranking, ..] 
    @param original_rank_vectors:  a list of the names of the attribute containing the human rank_strings, one ranking for each segment
    @type original_rank_vectors: [Ranking, ..]
    @keyword k: cut-off passed to the segment L{ndgc_err} function
    @type k: int 
    @return: a dictionary with the name of the metric and the respective result
    @rtype: {string, float}
    """
    ndgc_list = []
    err_list = []
    for predicted_rank_vector, original_rank_vector in zip(predicted_rank_vectors, original_rank_vectors):
        k = kwargs.setdefault('k', len(predicted_rank_vector))
        ndgc, err = segment.ndgc_err(predicted_rank_vector, original_rank_vector, k)
        ndgc_list.append(ndgc)
        err_list.append(err)
    avg_ndgc = average(ndgc_list)
    avg_err = average(err_list)
    return {'ndgc':avg_ndgc, 'err':avg_err}


def allmetrics(predicted_rank_vectors, original_rank_vectors,  **kwargs):
    stats = {}
    functions = [kendall_tau_set, mrr, best_predicted_vs_human, avg_predicted_ranked, avg_ndgc_err]
    for function in functions:
        stats.update(function(predicted_rank_vectors, original_rank_vectors, **kwargs))
    
    return stats
    
    
