'''
Created on Jul 21, 2011

@author: jogin
'''

from io.input.rankreader import RankReader


class InterAnnotatorAgreement(object):
    
    
    def get_combination_pairs(self, s):
        return [(s[i], s[j]) for i in range(len(s)) for j in range(i+1, len(s))]
                
        
    
    def get_pi(self, systems, ranking_files):
        """
        This function compares ranking difference between many ranking files and
        count from that a coefficient similar to Scott's pi. Further information about
        this can be found at Bojar et. al, A grain of Salt for the WMT Manual Evaluation, WMT 2011
        @param systems: names of 2 systems to be compared
        @type systems: tuple of strings
        @param rankingFile1: xml ranking file 1
        @type rankingFile1: string
        @param rankingFile2: xml ranking file 2
        @type rankingFile2: string
        @return scott_pi: computed Scott pi coefficient
        @type cohen_kappa: float
        """
        
        #create a list with parallelsentences indexed by sentence id, one dict for each judge
        
        
        datasets = [RankReader(ranking_file).get_dataset() for ranking_file in ranking_files]
        dataset = datasets[0]
        for i in range(1, len(datasets)):
            dataset.merge_dataset(datasets[i], {'rank' : 'rank_%d' % i }, ["sentence_id"])
        
        agreements = 0.00
        pairwise_rankings = 0.00
        equals = 0.00
        better = 0.00
        worse = 0.00
        rankings = 0.00
        
        #first get each sentence
        for ps in dataset.get_parallelsentences():
            pairwise_ps_set = ps.get_pairwise_parallelsentences()
            system_pairs = self.get_combination_pairs(systems)
            #then do comparisons per system pair
            for system_pair in system_pairs:
                pairwise_ps = pairwise_ps_set.get_pairwise_parallelsentence(system_pair)
                tgt1 = pairwise_ps.get_translations[0]
                tgt2 = pairwise_ps.get_translations[0]
                
                rank_names = ['rank_%d' % i for i in range(1,len(datasets))].append('rank')
                rank_name_pairs = self.get_combination_pairs(rank_names)
                
                #then compare the judgments of all annotators, in pairs as well
                for (rank_name_1, rank_name_2) in rank_name_pairs:  
                    
                    tgt1_rank1 = tgt1.get_attribute(rank_name_1)
                    tgt2_rank1 = tgt2.get_attribute(rank_name_1)
                    
                    tgt1_rank2 = tgt1.get_attribute(rank_name_2)
                    tgt2_rank2 = tgt2.get_attribute(rank_name_2)
                    
                    pairwise_rankings += 1
                    
                    if (tgt1_rank1 == tgt2_rank1 and tgt1_rank2 == tgt2_rank2) or \
                      (tgt1_rank1 > tgt2_rank1 and tgt1_rank2 > tgt2_rank2) or \
                      (tgt1_rank1 < tgt2_rank1 and tgt1_rank2 < tgt2_rank2):
                        agreements += 1
                
                for rank_name in rank_names:
                    tgt1_rank = tgt1.get_attribute(rank_name)
                    tgt2_rank = tgt2.get_attribute(rank_name_1)
                    rankings += 1
                    if tgt1_rank == tgt2_rank:
                        equals += 1
                    elif tgt1_rank < tgt2_rank:
                        worse += 1
                    elif tgt1_rank > tgt2_rank:
                        better += 1
            
        
        
        
        p_A = agreements / pairwise_rankings
                
        
        #p(E) = P(A>B)^2 + P(A=B)^2 + P(A<B)^2
        p_equal = equals / rankings
        p_better = better / rankings
        p_worse = worse / rankings
        p_E = p_equal^2 + p_better^2 + p_worse^2       
        
        scott_pi = (p_A - p_E) / (1 - p_E)
        
        
        
        return scott_pi
