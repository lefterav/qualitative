'''
Created on Nov 25, 2012

@author: dupo
'''
from math import log

def relevance(predicted_rank_value, original_rank_vector):
    """ convert the rank to a relevance score 0-1"""
    return (len(original_rank_vector) - predicted_rank_value) / len(original_rank_vector) 

def dcgp(predicted_rank_vector, original_rank_vector):
    assert(len(predicted_rank_vector), len(original_rank_vector))
    rel_1 = relevance(predicted_rank_vector[1], original_rank_vector)
    r = []
    for i, rank in enumerate(predicted_rank_vector):
        rel_i = relevance(rank, original_rank_vector)
        r.append(1.00*rel_i/log(i, 2))
    return rel_1 + sum(r)
    
def ndcgp(predicted_rank_vector, original_rank_vector):
    idcgp = dcgp(original_rank_vector, original_rank_vector)
    return 1.00*dcgp/idcgp

def mrr(predicted_rank_vector, original_rank_vector):
    assert(len(predicted_rank_vector), len(original_rank_vector))
    