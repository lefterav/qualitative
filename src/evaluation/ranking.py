'''
Created on Nov 25, 2012

@author: dupo
'''
from math import log
from operator import mul
from operator import itemgetter

def relevance_grade(predicted_rank_value, original_rank_vector):
    """ convert the rank to a relevance grade"""
    return (len(original_rank_vector) - predicted_rank_value)

def relevance_prob(predicted_rank_value, original_rank_vector):
    """ convert the rank to a relevance probability"""
    return (2.00**relevance_grade(predicted_rank_value, original_rank_vector)-1) / 2**len(original_rank_vector) 

def dcgp(predicted_rank_vector, original_rank_vector):
    assert(len(predicted_rank_vector) == len(original_rank_vector))
    rel_1 = relevance_grade(predicted_rank_vector[1], original_rank_vector)
    r = []
    for i, rank in enumerate(predicted_rank_vector, 1):
        rel_i = relevance_grade(rank, original_rank_vector)
        r.append(1.00*rel_i/log(i, 2))
    return rel_1 + sum(r)


def dcgp_log(predicted_rank_vector, original_rank_vector):
    assert(len(predicted_rank_vector) == len(original_rank_vector))
    r = []
    for i, rank in enumerate(predicted_rank_vector, 1):
        rel_i = relevance_grade(rank, original_rank_vector)    
        r.append((2.00**rel_i-1)/log(i+1, 2))
        
    return sum(r)

def ndcgp(predicted_rank_vector, original_rank_vector):
    idcgp = dcgp_log(original_rank_vector, original_rank_vector)
    pdcgp = dcgp_log(predicted_rank_vector, original_rank_vector)
    print " pdcgp / idcgp = {} / {} = ".format(pdcgp,idcgp),
    return 1.00*pdcgp/idcgp

def get_sorted_rank_tuples(rank_vector_1, rank_vector_2):
    #TODO: remove ties and keep only the highest respective rank
    rank_tuples = [(rank1, rank2) for rank1, rank2 in zip(rank_vector_1, rank_vector_2)]
    return sorted(rank_tuples, key=itemgetter(0))

def err(predicted_rank_vector, original_rank_vector):
    rank_tuples = get_sorted_rank_tuples(predicted_rank_vector, original_rank_vector)
    r = 0
    p = 1.00
    err = 0
    for stop_predicted_rank, stop_original_rank in rank_tuples:
        r+=1.00
        R = relevance_prob(stop_original_rank, original_rank_vector)
        err = err + p*R/r
        p = p*(1.00-R)
    return err

            
if __name__ == "__main__":
    predicted_rank_vector = [4, 1, 2, 5, 3]
    original_rank_vector = [2, 4, 5, 1, 3]
    print "ERR =", err(predicted_rank_vector, original_rank_vector)
    print "nDCG_p =", ndcgp(predicted_rank_vector, original_rank_vector)
    
    
    
    
        
     
    
    