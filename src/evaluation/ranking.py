'''
Created on Nov 25, 2012

@author: dupo
'''
from math import log
from operator import mul
from operator import itemgetter


def calculate_gains(r, l, verbose=False):
    """
    Calculate the gain for each one of the predicted ranks
    @param r: list of integers representing the predicted ranks
    @type r: [int, ...]
    @param l: list of integers containing the original ranks
    @type l: [int, ...]
    """
    n = len(l)
    expn = 2**n
    gains = [-1]*n 

    #added this line to get high gain for lower rank values
    r = r[::-1]
    for j in range(n):            
        gains[r[j]-1] = (2**l[j]-1.0)/expn

        if verbose:
            print "j={}\nr[j]={}\nl[j]={}\n".format(j,r[j],l[j]) 
            print "gains[j] = "
            print "\t(2**l[j]-1.0) / 2**n ="
            print "\t(2**{}-1.0) / 2**{}=".format(l[j], n)
            print "\t{} / {} =".format((2**l[j]-1.0),expn)
            print (2**l[j]-1.0)/expn
            print "gains = ",gains
    
    assert min(gains)>=0, 'Not all ranks present'
    return gains


def idcg(gains, k):
    """
    Calculate the Ideal Discounted Cumulative Gain, for the given vector of ranking gains
    @param gains: a list of integers pointing to the ranks 
    """
    #put the ranks in an order
    gains.sort()
    #invert the list
    gains = gains[::-1]
    ideal_dcg = sum([g/log(j+2) for (j,g) in enumerate(gains[:k])])
    return ideal_dcg

def ndgc_err(r, l, k):
    """
    Calculate the Normalized Discounted Cumulative Gain and the Expected Reciprocal Rank on a sentence level
    This follows the definition of U{DCG<http://en.wikipedia.org/wiki/Discounted_cumulative_gain#Cumulative_Gain>} 
    and U{ERR<http://research.yahoo.com/files/err.pdf>}, and the implementation of 
    U{Yahoo Learning to Rank challenge<http://learningtorankchallenge.yahoo.com/evaluate.py.txt>}     
    @param r: list of integers representing the predicted ranks
    @type r: [int, ...]
    @param l: list of integers containing the original ranks
    @type l: [int, ...]
    @return: a tuple containing the values for the two metrics
    @rtype: tuple(float,float)
    """
    # Number of documents    
    n = len(l)
    
    #make sure that the lists have the right dimensions 
    assert len(r)==n, 'Expected {} ranks, but got {}.'.format(n,len(r))    
    gains = calculate_gains(r, l)
        
    #ERR calculations
    p = 1.0    
    err = 0.0
    for j in range(n):    
        r = gains[j]
        err += p*r/(j+1.0)
        p *= 1-r
    
    #DCG calculation
    dcg = sum([g/log(j+2) for (j,g) in enumerate(gains[:k])])
    
    #NDCG calculation
    ideal_dcg = idcg(gains, k)
      
    if ideal_dcg:
        ndcg = dcg / ideal_dcg
    else:
        ndcg = 1.0
        
    return err, ndcg



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
    predicted_rank_vector = [1,2,3,4]
    original_rank_vector = [1, 2, 3, 4]
    dcg, err = ndgc_err(predicted_rank_vector, original_rank_vector, 5)
    print "ERR = {}\n nDCG_p = {}".format(dcg, err) 
    
    
    
    
        
     
    
    