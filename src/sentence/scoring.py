#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""

from dataset import DataSet
from multirankeddataset import MultiRankedDataset
from scipy.stats import spearmanr
from scipy.stats import kendalltau

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
        success = 0.00
        for parallesentence in self.parallelsentences:
            estimated_rank_vector = parallesentence.get_target_attribute_values(estimated_rank_name)
            original_rank_vector = parallesentence.get_target_attribute_values(original_rank_name)
            for i in range(len(estimated_rank_vector)):
                if estimated_rank_vector[i] == 1:
                    if original_rank_vector[i] == 1:
                        success += 1
                    break
        return success/len(self.parallelsentences)
                

    
    """
    @todo: clean references and delete
    """
    def get_kendall_tau(self, rank_name_1, rank_name_2):
        segment_tau = 0.00
        didnt = 0
        for parallesentence in self.parallelsentences:
            rank_vector_1 = parallesentence.get_target_attribute_values(rank_name_1)
            rank_vector_2 = parallesentence.get_target_attribute_values(rank_name_2)
            
            print "\t".join(rank_vector_1), 
            print "\t",
            print "\t".join(rank_vector_2),
            print "\t",
            tau = kendalltau(rank_vector_1, rank_vector_2)[0]
            if (tau >= -1 and tau <= 1):
                segment_tau += tau
                print tau
            else:
                didnt += 1
                print "-1"
        #print "Didn't %s" % didnt
        avg_tau = segment_tau / (len(self.parallelsentences) - didnt)
        return avg_tau
    

            
            
            
            
        
             
        
        
        
    
        
        