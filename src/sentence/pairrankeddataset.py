'''
Created on May 12, 2011

@author: Eleftherios Avramidis
'''

from dataset import DataSet

class PairRankedDataset:
    '''
    A data container that stores the entire dataset of parallel sentences, but internally this has been re-structured
    so that every multiple ranking judgment (e.g. 1-5) has been split into pairwise comparisons (1,2; 1,3; ...).
    Every set of pairwise comparisons has been mapped to the judgment id of the original multiple ranking judgment
    This allows for direct access to each judgment's pairwise elements    
    '''
    
    def __init__(self, dataset):
        """
        @param dataset: Initialize the class by converting an existing DataSet object
        @type dataset: sentence.dataset.DataSet
        """
        self.ranking_entries = {}
        self.ranking_entries = self._load_ranking_entries(dataset)
    
    def _load_ranking_entries(self, dataset):
        """
        convert the parallel sentences that exist in each multiple ranking judgment
        of the dataset and map them to the corresponding judgment id. 
        @param dataset: the dataset to be converted
        @type dataset: sentence.dataset.DataSet
        """
        ranking_entries = {}
        for judgement_id, parallelsentence in dataset.get_parallelsentences_with_judgment_ids().iteritems():
            #get the pairwise representation of the current ranking judgment 
            pairwise_parallel_sentences = parallelsentence.get_pairwise_parallelsentences()
            #add the pair into the dictionary mapped to the unique judgment id
            ranking_entries[judgement_id] = pairwise_parallel_sentences
        return ranking_entries
    
    def get_ranking_entry(self, judgement_id):
        return self.ranking_entries[judgement_id]
    
    def get_pairs_per_sentence_id(self):
        ps_sid = {}
        for judgment_id, pairwise_set in self.ranking_entries.iteritems():
            for  
            #get the id of the particular multiple ranking (judgment) or create a new one
            sentence_id = pairwise_set.get_compact_id()
            if not ps_sid.has_key(sentence_id):
                ps_sid[sentence_id] = []
            else:
                ps_sid[sentence_id].append(pairwise_set)
        return ps_sid      
            
    
    


class CompactPairRankedDataset:
    
    def __init__(self, pair_ranked_dataset):
        self.pairwise_rankings_per_sentence = self._merge_rankings_per_sentence(pair_ranked_dataset)
    

    def _merge_rankings_per_sentence(self, dataset):
        pairwise_comparisons_per_sentence = dataset.get_pairs_per_sentence_id()
        for sentence_id in pairwise_comparisons_per_sentence:
            pairwiseparallelsentences = pairwise_comparisons_per_sentence[sentence_id]
            for system_pair in pairwiseparallelsentences.
                
                 
            
        
        
        
    
    
            
            
            
        


        