'''
Created on May 12, 2011

@author: Eleftherios Avramidis
'''


from dataset import DataSet
from pairwiseparallelsentenceset import AnalyticPairwiseParallelSentenceSet, CompactPairwiseParallelSentenceSet


class PairwiseDataset:
    '''
    A data container that stores the entire dataset of parallel sentences, but internally this has been re-structured
    so that every multiple ranking judgment (e.g. 1-5) has been split into pairwise comparisons (1,2; 1,3; ...).
    Every set of pairwise comparisons has been mapped to the sentence id of the original source sentence
    This allows for direct access to pairwise elements of each sentence    
    '''
    def get_all_parallelsentence_sets(self):
        return self.pairwise_parallelsentence_sets.values()
    
    def get_parallelsentences(self):
        all_parallel_sentences = []
        for set in self.get_all_parallelsentence_sets():
            all_parallel_sentences.extend(set.get_parallelsentences())
        return all_parallel_sentences
    
    
    def get_sentence_ids(self):
        return self.pairwise_parallelsentence_sets.keys()
    
    def get_pairwise_parallelsentence_set(self, sentence_id):
        return self.pairwise_parallelsentence_sets[sentence_id]
    
    def get_pairwise_parallelsentence_sets(self):
        return self.pairwise_parallelsentence_sets
    
    def remove_ties(self):
        for set in self.pairwise_parallelsentence_sets.values():
            set.remove_ties()



class AnalyticPairwiseDataset(PairwiseDataset):
    
    def __init__(self, plain_dataset = DataSet()):
        """
        @param plain_dataset
        
        """
        self.pairwise_parallelsentence_sets = {}
        pairwise_parallelsentences_per_sid = {}
        
        #first group by sentence ID
        for parallelsentence in plain_dataset.get_parallelsentences():
            sentence_id = parallelsentence.get_compact_id()
            try:
                pairwise_parallelsentences_per_sid[sentence_id].extend(parallelsentence.get_pairwise_parallelsentences())
            except KeyError:
                pairwise_parallelsentences_per_sid[sentence_id] = parallelsentence.get_pairwise_parallelsentences()
        
        for sentence_id, pairwiseparallelsentences in pairwise_parallelsentences_per_sid.iteritems():
        #then convert each group to a Analytic Pairwise Parallel SentenceSet
            self.pairwise_parallelsentence_sets[sentence_id] = AnalyticPairwiseParallelSentenceSet(pairwiseparallelsentences)




class CompactPairwiseDataset(PairwiseDataset):
    
    def __init__(self, analytic_pairwise_dataset = AnalyticPairwiseDataset()):
        self.pairwise_parallelsentence_sets = {}
        for sentence_id, analytic_pairwise_parallelsentence_set in analytic_pairwise_dataset.get_pairwise_parallelsentence_sets().iteritems():
            self.pairwise_parallelsentence_sets[sentence_id] = analytic_pairwise_parallelsentence_set.get_compact_pairwise_parallelsentence_set()
        
        
        
        
        
        



#class PairRankedDataset:
#    '''
#    A data container that stores the entire dataset of parallel sentences, but internally this has been re-structured
#    so that every multiple ranking judgment (e.g. 1-5) has been split into pairwise comparisons (1,2; 1,3; ...).
#    Every set of pairwise comparisons has been mapped to the judgment id of the original multiple ranking judgment
#    This allows for direct access to each judgment's pairwise elements    
#    '''
#    
#    def __init__(self, dataset):
#        """
#        @param dataset: Initialize the class by converting an existing DataSet object
#        @type dataset: sentence.dataset.DataSet
#        """
#        self.pairwise_parallelsentence_sets = [parallelsentence.get_pairwise_parallelsentence_set() for parallelsentence in dataset.get_parallelsentence()]
#        
#    
#    def get_parallelsentences(self):
#        for pairwise_parallelsentence_sets
#        return [parallelsentence for parallelsentence in ]
        #self.ranking_entries = self._load_ranking_entries(dataset)
    
#    def _load_ranking_entries(self, dataset):
#        """
#        convert the parallel sentences that exist in each multiple ranking judgment
#        of the dataset and map them to the corresponding judgment id. 
#        @param dataset: the dataset to be converted
#        @type dataset: sentence.dataset.DataSet
#        """
#        ranking_entries = {}
#        for judgement_id, parallelsentence in dataset.get_parallelsentences_with_judgment_ids().iteritems():
#            #get the pairwise representation of the current ranking judgment 
#            pairwise_parallel_sentences = parallelsentence.get_pairwise_parallelsentence_set()
#            #add the pair into the dictionary mapped to the unique judgment id
#            ranking_entries[judgement_id] = pairwise_parallel_sentences
#        return ranking_entries
    
#    def get_ranking_entry(self, judgement_id):
#        return self.pairwise_parallelsentence_set[judgement_id]
    
#    def get_pairs_per_sentence_id(self):
#        ps_sid = {}
#        for pairwise_parallelsentence_set in self.pairwise_parallelsentence_sets:
#            for pairwise_parallelsentence in pairwise_parallelsentence_set.get_parallelsentences():
#                #get the id of the particular multiple ranking (judgment) or create a new one
#                sentence_id = pairwise_parallelsentence.get_compact_id()
#                if not ps_sid.has_key(sentence_id):
#                    ps_sid[sentence_id] = [pairwise_parallelsentence]
#                else:
#                    ps_sid[sentence_id].append(pairwise_parallelsentence)
#        return ps_sid      
            
    
    



                
#        self.pairwise_rankings_per_sentence = pair_ranked_dataset.get_pairs_per_sentence_id() 
#        
#        self._merge_rankings(pair_ranked_dataset)
#    
#
#    def _merge_rankings(self, dataset):
#        pairwise_comparisons_per_sentence = dataset.get_pairs_per_sentence_id()
#        merged_pairwiseparallelsentences = []
#        #merging has to happen only between the pairwise comparisons of outputs that originate from the same source sentence
#        for sentence_id, pairwiseparallelsentences in pairwise_comparisons_per_sentence.iteritems():
#            merged_pairwiseparallelsentence = self._merge_rankings_per_sentence(pairwiseparallelsentences)
#            
#    def _merge_rankings_per_sentence(self, pairwiseparallelsentences):
#        [(pairwiseparallelsentence.get_system_names() for pairwiseparallelsentence in pairwiseparallelsentences]:
#            
#            
#            
#            for system_pair in set
#                relevant_pairs = [pairwiseparallelsentence.get_pairwise_parallelsentence(system_pair) for pairwiseparallelsentence in pairwiseparallelsentences]
#                merged_pair = self.merge(relevant_pairs)
#                 
#            
        
        
        
    
    
            
            
            
        


        