#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""

from dataset import DataSet
from multirankeddataset import MultiRankedDataset
import logging


def get_kendall_tau(predicted_rank_vector, original_rank_vector, **kwargs):
    """
    Calculates Kendall tau of predicted vs human ranking according to WMT12 (Birch et. al 2012)
    @param predicted_pairs: a list of integers representing the predicted ranks
    @type predicted_rank_name: str 
    @param original_rank_name: the name of the attribute containing the human rank
    @type original_rank_name: str
    @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
    @rtype: tuple(float, float)
    """
    
    import numpy as np
    from scipy import special
    import itertools
    
    penalize_ties = kwargs.setdefault("penalize_ties", True)
    
    #the following will give positive int, if i > j, negative int if i < j and 0 for ties
    predicted_pairs = [int(i)-int(j) for i, j in itertools.combinations(predicted_rank_vector, 2)]
    original_pairs = [int(i)-int(j) for i, j in itertools.combinations(original_rank_vector, 2)]
    all_pairs_count = len(predicted_pairs)
    
    concordant_count = 0
    discordant_count = 0
    
    #count concordant and discordant pairs
    for original_pair, predicted_pair in zip(original_pairs, predicted_pairs):
        if original_pair * predicted_pair > 0 or (predicted_pair == 0 and original_pair == 0):
            concordant_count += 1
        #if there is a tie on the predicted side, this is counted as two discordants pairs
        elif predicted_pair == 0 and penalize_ties:
            discordant_count += 2
            concordant_count -= 1
        elif predicted_pair == 0 and not penalize_ties:
            discordant_count += 1
        #if there is a tie on the original human annotation, this is not counted
        elif original_pair == 0:
            pass
        #and finally when there is disagreement without a tie 
        else:
            discordant_count += 1
    
    logging.debug("conc = %d, disc= %s", concordant_count, discordant_count) 
    tau = 1.00 * (concordant_count - discordant_count) / all_pairs_count
    
    #probability of independence hypothesis
    try:
        svar = (4.0 * all_pairs_count + 10.0) / (9.0 * all_pairs_count * (all_pairs_count - 1))
    except:
        svar = 1
    try: 
        z = tau / np.sqrt(svar)
    except:
        z = 1
    prob = special.erfc(np.abs(z) / 1.4142136)
    print tau
    return tau, prob




class Scoring(MultiRankedDataset):
    """
    classdocs
    """
    
    def get_systems_scoring_from_segment_ranks(self, rank_attribute_name):
        
        """
        Provides a performance score for every system. The score is the percentage of times the system
        performed better than all other systems or equally to the systems that performed better than all other systems
        @param rank_attribute_name: the name of the target sentence attribute which contains the rank value, that we compare upon 
        Smaller rank means better system.  
        @type rank_attribute_name: string
        @return A map of the system names and their performance percentage
        """
        systems_performance = {}
        for parallelsentence in self.parallelsentences:
            rank_per_system = {}
            #first sort the ranks by system
            for target in parallelsentence.get_translations():
                system = target.get_attribute("system")
                rank = int(float(target.get_attribute(rank_attribute_name)))
                rank_per_system[system] = rank
            #then count the times a system performs as best
            for system in rank_per_system:
                if rank_per_system[system] == min(rank_per_system.values()):
                    try:
                        systems_performance[system] += 1
                    except KeyError:
                        systems_performance[system] = 1
        #finally calculate the percentage that each system, scored as best
        for system in systems_performance:
            systems_performance[system] = 1.00 * systems_performance[system] / len(self.parallelsentences)
        return systems_performance
    
    def get_spearman_correlation(self, rank_name_1, rank_name_2):
        from scipy.stats import spearmanr
        """
        Calculates the system-level Spearman rank correlation given two sentence-level features, i.e. 
        the human and the estimated rank of each parallelsentence 
        @param rank_name_1: the name of the target sentence attribute containing the first rank value
        @type rank_name_1: string
        @param rank_name_2: the name of the target sentence attribute containing the second rank value
        @type rank_name_2: string
        @return the Spearman correlation rho and p value
        """
        systems_evaluation_1 = self.get_systems_scoring_from_segment_ranks(rank_name_1)
        systems_evaluation_2 = self.get_systems_scoring_from_segment_ranks(rank_name_2)
        #print systems_evaluation_1
        #print systems_evaluation_2
        rank_evaluation_1 = []
        rank_evaluation_2 = []
        for (system, rank_1) in systems_evaluation_1.items():
            rank_evaluation_1.append(rank_1)
            rank_2 = systems_evaluation_2[system]
            rank_evaluation_2.append(rank_2)
        #print "rank------" 
        #print rank_evaluation_1
        #print rank_evaluation_2
        return spearmanr(rank_evaluation_1, rank_evaluation_2)
    
    def get_kendall_tau_vector(self, rank_name_1, rank_name_2):
        from scipy.stats import kendalltau

        taus = []
        pis = []
        for parallesentence in self.parallelsentences:
            rank_vector_1 = parallesentence.get_target_attribute_values(rank_name_1)
            rank_vector_2 = parallesentence.get_target_attribute_values(rank_name_2)
            
            fullscore = kendalltau(rank_vector_1, rank_vector_2)
            tau = fullscore[0]
            pi = fullscore[1]
            taus.append(tau)
            pis.append(pi)
        return taus, pis
    
    def get_kendall_tau_avg(self, rank_name_1, rank_name_2):
        taus, pis = self.get_kendall_tau_vector(rank_name_1, rank_name_2)
        avg = sum(taus)/len(taus)
        pi = min(pis)
        return avg, pi
    
    def get_kendall_tau_freq(self, rank_name_1, rank_name_2):
        taus = self.get_kendall_tau_vector(rank_name_1, rank_name_2)[0]
        frequency = {}
        for tau in taus:
            try:
                frequency[tau] += 1
            except KeyError:
                frequency[tau] = 0
        return frequency 
            
    def selectbest_accuracy(self, estimated_rank_name, original_rank_name):
        truepositive_withfirsteffort = 0.00
        truepositive_withanyeffort = 0.00
        pairwise_comparisons = 0.00
        for parallesentence in self.parallelsentences:
            estimated_rank_vector = parallesentence.get_target_attribute_values(estimated_rank_name)
            original_rank_vector = parallesentence.get_target_attribute_values(original_rank_name)
            
            true_positive = 0.00
            false_positive = 0.00
            alreadyfoundfirst = False
            
            for i in range(len(estimated_rank_vector)):
                if int(estimated_rank_vector[i]) == 1:
                    pairwise_comparisons += 1
                    if int(original_rank_vector[i]) == 1:
                        true_positive += 1
                        if not alreadyfoundfirst:
                            truepositive_withfirsteffort +=1
                    else:
                        false_positive += 1
                    alreadyfoundfirst = True
            if true_positive > 0 : 
                truepositive_withanyeffort +=1
            

                    
        accuracy_firsteffort = truepositive_withfirsteffort/len(self.parallelsentences)
        accuracy_anyeffort = truepositive_withanyeffort / len(self.parallelsentences)
        return (accuracy_firsteffort, accuracy_anyeffort)
        
                

       

    
    def get_kendall_tau(self, predicted_rank_name, original_rank_name, **kwargs):
        """
        Calculates Kendall tau of predicted vs human ranking according to WMT12 (Birch et. al 2012)
        @param predicted_rank_name: the name of the attribute containing the predicted rank
        @type predicted_rank_name: str 
        @param original_rank_name: the name of the attribute containing the human rank
        @type original_rank_name: str
        @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
        @rtype: tuple(float, float)
        """
        import itertools
        import numpy as np
        
        taus = []
        probs = []
        for parallesentence in self.parallelsentences:
            predicted_rank_vector = parallesentence.get_target_attribute_values(predicted_rank_name)
            original_rank_vector = parallesentence.get_target_attribute_values(original_rank_name)
           
            tau, prob = get_kendall_tau(predicted_rank_vector, original_rank_vector, **kwargs)
            taus.append(tau)
            probs.append(prob)            
                 
        return np.average(tau), np.product(prob)
    
    
    
    def get_kendall_tau_b(self, predicted_rank_name, original_rank_name):
        """
        Calculates Kendall tau beta of predicted vs human ranking according to the Knight (1966) 
        [scipy implementation] taking account of ties    
        @param predicted_rank_name: the name of the attribute containing the predicted rank
        @type predicted_rank_name: str 
        @param original_rank_name: the name of the attribute containing the human rank
        @type original_rank_name: str
        @return: the Kendall tau score and the probability for the null hypothesis of X and Y being independent
        @rtype: tuple(float, float)
        """
        from scipy.stats import kendalltau
        from numpy import isnan

        segment_tau = 0.00
        segment_pi = 1.00
        for parallesentence in self.parallelsentences:
            predicted_rank_vector = parallesentence.get_target_attribute_values(predicted_rank_name)
            original_rank_vector = parallesentence.get_target_attribute_values(original_rank_name)
            
            print "[{0}]".format(" , ".join(predicted_rank_vector)) 
            print "[{0}]".format(" , ".join(original_rank_vector))
            
            #if had this denominator error, just provide the result of smoothing
            tau, pi = kendalltau(original_rank_vector, predicted_rank_vector)
            if isnan(tau) or isnan(pi):
                tau = 0.00
                pi = 1.00

            segment_tau += tau
            segment_pi *= pi
            print tau
        
        avg_tau = 1.00 * segment_tau / len(self.parallelsentences)
        
        
        print "Avg tau:  segment_tau / len(self.parallelsentences) \n= {0} / {1}  \n= {2}".format(segment_tau, len(self.parallelsentences), avg_tau)
        return avg_tau, segment_pi
    

def regenerate_tau():
    """
    Test script which should be run particularly from with the separate experiment folders, 
    in order to reproduce results without re-executing the experiment script
    """
    
    from io_utils.input.jcmlreader import JcmlReader
    d = JcmlReader("testset.reconstructed.hard.jcml").get_dataset()
    scoringset = Scoring(d)
    scoringset.get_kendall_tau("rank_hard", "rank")
            
            
        
             
        
        
        
    
        
        