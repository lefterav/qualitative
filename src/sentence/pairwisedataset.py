'''
Created on May 12, 2011

@author: Eleftherios Avramidis
'''


from dataset import DataSet
from pairwiseparallelsentenceset import AnalyticPairwiseParallelSentenceSet, CompactPairwiseParallelSentenceSet


class PairwiseDataset(DataSet):
    '''
    A data container that stores the entire dataset of parallel sentences, but internally this has been re-structured
    so that every multiple ranking judgment (e.g. 1-5) has been split into pairwise comparisons (1,2; 1,3; ...).
    Every set of pairwise comparisons has been mapped to the sentence id of the original source sentence
    This allows for direct access to pairwise elements of each sentence   
    @ivar pairwise_parallelsentence_sets: A dictionary which keeps the pairwise sentences per (original) sentence id
    @type pairwise_parallelsentence_sets: {str: }
    '''
    def get_all_parallelsentence_sets(self):
        return self.pairwise_parallelsentence_sets.values()
    
    def get_parallelsentences(self):
        all_parallel_sentences = []
        for sentence_set in self.get_all_parallelsentence_sets():
            all_parallel_sentences.extend(sentence_set.get_parallelsentences())
        return all_parallel_sentences
    
     
    
    def get_sentence_ids(self):
        return self.pairwise_parallelsentence_sets.keys()
    
    def get_pairwise_parallelsentence_set(self, sentence_id):
        return self.pairwise_parallelsentence_sets[sentence_id]
    
    def get_pairwise_parallelsentence_sets(self):
        return self.pairwise_parallelsentence_sets
    
    def remove_ties(self):
        """
        It removes the ties from the current data set
        @return: the number of ties removed (helpful for testing)
        @rtype: int
        """
        removed_ties = 0
        for myset in self.pairwise_parallelsentence_sets.values():
            removed_ties += myset.remove_ties()
        #filter out sentences where nothing is left
        self.pairwise_parallelsentence_sets = dict([(id, ps) for (id, ps) in self.pairwise_parallelsentence_sets.iteritems() if ps.length() > 0])
        return removed_ties


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
                pairwise_parallelsentences_per_sid[sentence_id].extend(parallelsentence.get_pairwise_parallelsentences(False))
            except KeyError:
                pairwise_parallelsentences_per_sid[sentence_id] = parallelsentence.get_pairwise_parallelsentences(False)
        
        for sentence_id, pairwiseparallelsentences in pairwise_parallelsentences_per_sid.iteritems():
        #then convert each group to a Analytic Pairwise Parallel SentenceSet
            self.pairwise_parallelsentence_sets[sentence_id] = AnalyticPairwiseParallelSentenceSet(pairwiseparallelsentences)


class CompactPairwiseDataset(PairwiseDataset):  
    def __init__(self, analytic_pairwise_dataset = AnalyticPairwiseDataset()):
        self.pairwise_parallelsentence_sets = {}
        for sentence_id, analytic_pairwise_parallelsentence_set in analytic_pairwise_dataset.get_pairwise_parallelsentence_sets().iteritems():
            self.pairwise_parallelsentence_sets[sentence_id] = analytic_pairwise_parallelsentence_set.get_compact_pairwise_parallelsentence_set()
        
    def get_multiclass_set(self):
        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence()
            multirank_parallelsentences.append(multirank_parallelsentence)
        try:
            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("id")))
        except:
            pass
        return DataSet(multirank_parallelsentences)
        
    def get_single_set_with_hard_ranks(self, critical_attribute=None, new_rank_name=None):

        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence(critical_attribute, new_rank_name)
            multirank_parallelsentences.append(multirank_parallelsentence)
        try:
            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("id")))
        except:
            pass
        return DataSet(multirank_parallelsentences)
    
    
    
    def get_single_set_with_soft_ranks(self, attribute1="", attribute2="", critical_attribute="rank_soft_predicted", new_rank_name = None):
        '''
        Reconstructs the original data set, with only one sentence per entry.
        @return: Simple dataset that contains the simplified parallel sentences
        @rtype: L{DataSet}
        '''
        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence_with_soft_ranks(attribute1, attribute2, critical_attribute, new_rank_name)
            multirank_parallelsentences.append(multirank_parallelsentence)
        try:
            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("id")))
        except:
            pass
        return DataSet(multirank_parallelsentences)

    
class FilteredPairwiseDataset(CompactPairwiseDataset):
    def __init__(self, analytic_pairwise_dataset = AnalyticPairwiseDataset(), threshold = 1.00):    
        self.pairwise_parallelsentence_sets = {}
        for sentence_id, analytic_pairwise_parallelsentence_set in analytic_pairwise_dataset.get_pairwise_parallelsentence_sets().iteritems():
            self.pairwise_parallelsentence_sets[sentence_id] = analytic_pairwise_parallelsentence_set.get_filtered_pairwise_parallelsentence_set(threshold)



        
        



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
        
        
        
    
    
            
            
            
        


        