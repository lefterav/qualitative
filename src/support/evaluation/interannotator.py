# coding=utf-8
'''
Created on Jul 21, 2011

@author: jogin
'''

from io.input.rankreader import RankReader


class InterAnnotatorAgreement(object):
    
    
    def get_combination_pairs(self, s, directed = False):
        if not directed:
            return [(s[i], s[j]) for i in range(len(s)) for j in range(i+1, len(s))]
        else:
            oneway = [(s[i], s[j]) for i in range(len(s)) for j in range(i+1, len(s))]
            reversed = [(s[j], s[i]) for i in range(len(s)) for j in range(i+1, len(s))]
            oneway.extend(reversed)
            return oneway
                
        
    
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
            dataset.merge_dataset(datasets[i], {'rank' : 'rank_%d' % i }, ["id"])
        
        agreements = 0.0000
        pairwise_rankings = 0.0000
        equals = 0.0000
        better = 0.0000
        worse = 0.0000
        rankings = 0.0000
        
        #first get each sentence
        for ps in dataset.get_parallelsentences():
            pairwise_ps_set = ps.get_pairwise_parallelsentences(False)
            system_pairs = self.get_combination_pairs(systems, True)
            #then do comparisons per system pair
            for system_pair in system_pairs:
                pairwise_ps = pairwise_ps_set.get_pairwise_parallelsentence(system_pair)
                
                #we are looking for directed pairs. If pair does not exist, go to the next one and don't collect any counts
                if not pairwise_ps:
                    continue
                
                tgt1 = pairwise_ps.get_translations()[0]
                tgt2 = pairwise_ps.get_translations()[1]
                
                rank_names = ['rank_%d' % i for i in range(1,len(datasets))]
                rank_names.append('rank')
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
                
                #counts for the empirical expected agreement
                for rank_name in rank_names:
                    tgt1_rank = tgt1.get_attribute(rank_name)
                    tgt2_rank = tgt2.get_attribute(rank_name)
                    rankings += 1
                    if tgt1_rank == tgt2_rank:
                        equals += 1
                    elif tgt1_rank < tgt2_rank:
                        worse += 1
                    elif tgt1_rank > tgt2_rank:
                        better += 1
            
        
        
        
        p_A = agreements / pairwise_rankings
        print "p(A) = %.3f / %.3f = %.3f \n" % (agreements, pairwise_rankings, p_A)
                        
        
        #p(E) = P(A>B)^2 + P(A=B)^2 + P(A<B)^2
        p_equal = equals / rankings
        print "p(=) = %.3f / %.3f = %.3f" % (equals, rankings, p_equal)
        
        p_better = better / rankings
        print "p(>) = %.3f / %.3f = %.3f" % (better, rankings, p_better)
        
        p_worse = worse / rankings
        print "p(<) = %.3f / %.3f = %.3f" % (worse, rankings, p_worse)
        
        p_E = p_equal ** 2 + p_better ** 2 + p_worse ** 2       
        print "\np(E) = p(=)² + p(<)² + p(>)² \n\t = %.3f² + %.3f² + %.3f² \n\t = %.3f + %.3f + %.3f \n\t = %.3f" % (p_equal, p_better, p_worse, p_equal**2, p_better**2, p_worse**2 , p_E)

        scott_pi = (p_A - p_E) / (1 - p_E)
        print "π = (p(A) - p(E)) / (1 - p(E)) \n\t = (%.3f - %.3f) / (1 - %.3f) \n\t = %.3f" % (p_A, p_E, p_E, scott_pi)
        
        
        return scott_pi
    
systems = [  "trados", "lucy", "moses", "google"  ]

ranking_files = [  "/home/elav01/taraxu_data/r1/results/19-1-WMT08-de-en-ranking.xml", "/home/elav01/taraxu_data/r1/results/6-1-WMT08-de-en-ranking.xml"]

#ranking_files = ["/home/elav01/taraxu_data/r1/results/10-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/15-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/25-1-WMT08-en-de-ranking.xml"]


print InterAnnotatorAgreement().get_pi(systems, ranking_files)
