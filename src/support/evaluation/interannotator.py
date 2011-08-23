'''
Created on Jul 21, 2011

@author: jogin
'''

from io.input.rankreader import RankReader


class InterAnnotatorAgreement(object):
    
    
    def index_by_sentence_id(self, parallelsentences):
        """
        Produces a dictionary out of a parallelsentences list. The key of the dictionary is the sentence_id
        @param parallesentences The list of the parallelsentences to be indexed by sentence id
        @type [Parallelsentence]
        @return: a dictionary indexing the sentences
        @rtype: dict
        """
        dict = {}
        for parallelsentence in parallelsentences:
            key = parallelsentence.get_attribute("sentence_id")
            dict[key] = parallelsentence
        return dict
    
    def get_sentence_ids(self, dict):
        """
        Retrieves the sentence ids appearing into many different judgment files and delivers them into one list
        """
        sentence_ids = set()
        for indexed_judgment in dict:
            sentence_ids.union(set(indexed_judgment.keys()))
        return list(sentence_ids)
    
    
    def get_system_pairs(self, s):
        return [(s[i], s[j]) for i in range(len(s)) for j in range(i+1, len(s))]
                
        
    
    def get_cohen_kappa(self, systems, ranking_files):
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
        indexed_judgements = [self.index_by_sentence_id(RankReader(ranking_file).get_parallelsentences()) for ranking_file in ranking_files]
        sentence_ids = self.get_sentence_ids(indexed_judgements)
        

        equal_all = 0.000
        better_all = 0.000
        worse_all = 0.000
        total = 0.000
        
        equals_single = 0.000
        better_single = 0.000
        worse_single = 0.000
        
        agreement = 0.000
    
        #iterate throug all the sentences       
        for sentence_id in sentence_ids:
            pairwise_parallelsentences_per_judge = [indexed_file[sentence_id].get_pairwise_parallelsentences() for indexed_file in indexed_judgements]
            #break that into pairwise comparisons for every pair of system names 
            for system_pair in self.get_system_pairs(systems):
                
                if len(pairwise_parallelsentences_per_judge) < 2:
                    print "Error: cannot measure agreement, when having less than two judgments for this comparison with sentence_id = %s and systems = (%s, %s) " % (sentence_id, system_pair[0], system_pair[1]) 
                
                #set a default value of True and change to False into the loop of judgments, when there is a disagreement
                equals = True
                better = True
                worse = True
                total += 1
                annotated = 0

                
                #this will loop over the different judgments for the comparison of the current 2 output pairs
                for pairwise_ps in pairwise_parallelsentences_per_judge:
                    ps = pairwise_ps.get_pairwise_parallelsentence(system_pair) 
                    rank1 = ps.get_translations()[0].get_attribute('rank')
                    rank2 = ps.get_translations()[1].get_attribute('rank')
                
                    if rank1 != rank2: 
                        equals = False
                    if not (rank1 > rank2):
                        better = False
                    if not (rank1 < rank2):
                        worse = False
                    
                    annotated += 1
                    
                    if rank1 ==  rank2:
                        equals_single += 1
                    elif rank1 > rank2:
                        better_single += 1
                    elif rank1 < rank2:
                        worse_single += 1
                    
                        
                        
                
                #if all judges had the same verdict for all pairwise comparisons
                if equals or better or worse:
                    agreement += 1
                #count occurences for every comparison option
                if equals:
                    equal_all += 1
                elif better:
                    better_all += 1
                elif worse:
                    worse_all += 1
                    
        
        #strict per-sentence agreement Scott's pi
        p_A = agreement / total
        
        
        #p(E) = P(A>B)^2 + P(A=B)^2 + P(A<B)^2
        p_equal = equal_all / total
        p_better = better_all / total
        p_worse = worse_all / total
        p_E = p_equal^2 + p_better^2 + p_worse^2       
        
        scott_pi = (p_A - p_E) / (1 - p_E)
        
        #loose per-sentence agreement Fleiss' kappa
        
        
        return scott_pi
