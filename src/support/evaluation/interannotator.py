# coding=utf-8
'''
Created on Jul 21, 2011

@author: jogin
'''

from io.input.rankreader import RankReader



    
    
def get_combination_pairs(s, directed = False):
    if not directed:
        return [(s[i], s[j]) for i in range(len(s)) for j in range(i+1, len(s))]
    else:
        return [(s[j], s[i]) for i in range(len(s)) for j in range(len(s)) if i != j]
     
        
    

def get_pi_calculation(systems, ranking_files, reader = RankReader):
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
    
    calculation = []
    datasets = [reader(ranking_file).get_dataset() for ranking_file in ranking_files]
    dataset = datasets[0]
    #merge all datasets (i.e. users) in one dataset, where each sentence 
    #appears only once, and has all judgments by all annotators 
    for i in range(1, len(datasets)):
        dataset.merge_dataset(datasets[i], {'rank' : 'rank_%d' % i }, ["sentence_id"], True)
    
    agreements = 0.0000
    pairwise_rankings = 0.0000
    equals = 0.0000
    better = 0.0000
    worse = 0.0000
    rankings = 0.0000
    
    #first get each sentence
    for ps in dataset.get_parallelsentences():
        if not ps:
            continue
        pairwise_ps_set = ps.get_pairwise_parallelsentences(False)
        system_pairs = get_combination_pairs(systems, True)
        #then do comparisons per system pair
        for system_pair in system_pairs:
            pairwise_ps = pairwise_ps_set.get_pairwise_parallelsentence(system_pair)
            
            #we are looking for directed pairs. If pair does not exist, go to the next one and don't collect any counts
            if not pairwise_ps:
                continue
            
            tgt1 = pairwise_ps.get_translations()[0]
            tgt2 = pairwise_ps.get_translations()[1]
            
            #get a list with the ranks, and then all the possible pairs
            rank_names = ['rank_%d' % i for i in range(1,len(datasets))]
            rank_names.append('rank')
            rank_name_pairs = get_combination_pairs(rank_names)
            
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
    calculation.append("p(A) = %.3f / %.3f = %.3f \n" % (agreements, pairwise_rankings, p_A))
                    
    
    #p(E) = P(A>B)^2 + P(A=B)^2 + P(A<B)^2
    p_equal = equals / rankings
    calculation.append("p(=) = %.3f / %.3f = %.3f" % (equals, rankings, p_equal))
    
    p_better = better / rankings
    calculation.append("p(>) = %.3f / %.3f = %.3f" % (better, rankings, p_better))
    
    p_worse = worse / rankings
    calculation.append("p(<) = %.3f / %.3f = %.3f" % (worse, rankings, p_worse))
    
    p_E = p_equal ** 2 + p_better ** 2 + p_worse ** 2       
    calculation.append("\np(E) = p(=)² + p(<)² + p(>)² \n\t = %.3f² + %.3f² + %.3f² \n\t = %.3f + %.3f + %.3f \n\t = %.3f" % (p_equal, p_better, p_worse, p_equal**2, p_better**2, p_worse**2 , p_E))

    scott_pi = (p_A - p_E) / (1 - p_E)
    calculation.append("π = (p(A) - p(E)) / (1 - p(E)) \n\t = (%.3f - %.3f) / (1 - %.3f) \n\t = %.3f" % (p_A, p_E, p_E, scott_pi))
    calculation = "\n".join(calculation)
    
    return scott_pi, calculation



def get_pi(systems, ranking_files, reader = RankReader):
    pi, calc = get_pi_calculation(systems, ranking_files, reader)
    #print calc
    return pi



def print_pairwise_pis(systems, ranking_files):
    print "systems & pi \\\\ \hline"
    pairwise_systems = get_combination_pairs(systems, False)
    for pairwise_system in pairwise_systems:
        print ", ".join(pairwise_system), "&", round(get_pi(pairwise_system, ranking_files), 3), "\\\\"
        
    print "\ndatasets & pi \\\\ \hline"
    pairwise_rankers = get_combination_pairs(ranking_files, False)
    for pairwise_ranker in pairwise_rankers:
        print ", ".join(pairwise_ranker), "&", round(get_pi(systems, pairwise_ranker), 3), "\\\\"


def print_total_pis(systems, ranking_file_sets):
    print "\nlanguage pair & pi \\\\ \hline"
    for langpair, ranking_files in ranking_file_sets:
        print langpair , "&" , round(get_pi(systems, ranking_files), 3), " \\"
    return

systems = [  "lucy", "moses", "trados", "google"  ]

ranking_files_deen = [  "/home/elav01/taraxu_data/r1/results/19-1-WMT08-de-en-ranking.xml", "/home/elav01/taraxu_data/r1/results/6-1-WMT08-de-en-ranking.xml"]
ranking_files_ende = ["/home/elav01/taraxu_data/r1/results/10-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/15-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/25-1-WMT08-en-de-ranking.xml"]
#ranking_files_ende = ["/home/elav01/taraxu_data/ml4hmt-submissions/rankings/1-ML4HMT-DCU-Task-es-en-ranking.xml","/home/elav01/taraxu_data/ml4hmt-submissions/rankings/2-ML4HMT-DFKI-Task-es-en-ranking.xml","/home/elav01/taraxu_data/ml4hmt-submissions/rankings/3-ML4HMT-BM-Task-es-en-ranking.xml"]
 
#ranking_files = ["/home/elav01/taraxu_data/r1/results/10-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/15-1-WMT08-en-de-ranking.xml"]
#ranking_files = ["/home/elav01/taraxu_data/r1/results/10-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/25-1-WMT08-en-de-ranking.xml"]
#ranking_files = ["/home/elav01/taraxu_data/r1/results/15-1-WMT08-en-de-ranking.xml", "/home/elav01/taraxu_data/r1/results/25-1-WMT08-en-de-ranking.xml"]

print "Overall correlations scores"
print print_total_pis(systems, [("de-en", ranking_files_deen), ("en-de", ranking_files_ende)])
#print print_total_pis(systems, [("es-en", ranking_files_ende)])

print "English to German\n"
print print_pairwise_pis(systems, ranking_files_ende)

print "German to English\n"
print print_pairwise_pis(systems, ranking_files_deen)



