'''
Created on May 12, 2011

@author: Eleftherios Avramidis
'''


from dataset import DataSet
from pairwiseparallelsentenceset import AnalyticPairwiseParallelSentenceSet, CompactPairwiseParallelSentenceSet
from pairwiseparallelsentence import PairwiseParallelSentence
import sys
from collections import OrderedDict


class PairwiseDataset(DataSet):
    '''
    Abstract class that defines the data container that stores the entire dataset of parallel sentences, but internally this has been re-structured
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
        self.pairwise_parallelsentence_sets = OrderedDict([(sid, ps) for (sid, ps) in self.pairwise_parallelsentence_sets.iteritems() if ps.length() > 0])
        return removed_ties




class RevertablePairwiseDataset(PairwiseDataset):
    """
    Abstract class for pairwise datasets whose internal structure allows them to be reconstructed back to multi-class sets
    It pre-supposes that there are unique pairs per entry (indexable either by judgment_id or sentence_id)
    """
    
    def get_multiclass_set(self):
        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence()
            multirank_parallelsentences.append(multirank_parallelsentence)
#        try:
#            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("id")))
#        except:
#            pass
        return DataSet(multirank_parallelsentences)
        
    def get_single_set_with_hard_ranks(self, critical_attribute=None, new_rank_name=None, **kwargs):

        sort_attribute = kwargs.setdefault("sort_attribute", None)
        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence(critical_attribute, new_rank_name, False)
            multirank_parallelsentences.append(multirank_parallelsentence)
        if sort_attribute:
            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute(sort_attribute)))
        else:
#            try:
#                multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("judgement_id")))
#            except:
            pass
        return DataSet(multirank_parallelsentences)
    
    def get_single_set_with_soft_ranks(self, attribute1="", attribute2="", critical_attribute="rank_soft_predicted", new_rank_name = None, **kwargs):
        '''
        Reconstructs the original data set, with only one sentence per entry.
        @return: Simple dataset that contains the simplified parallel sentences
        @rtype: L{DataSet}
        '''
        sort_attribute = kwargs.setdefault("sort_attribute", None)
        multirank_parallelsentences = []
        for sentence_id in self.pairwise_parallelsentence_sets:
            pairwise_parallelsentence_set = self.pairwise_parallelsentence_sets[sentence_id]
            multirank_parallelsentence = pairwise_parallelsentence_set.get_multiranked_sentence_with_soft_ranks(attribute1, attribute2, critical_attribute, new_rank_name)
            multirank_parallelsentences.append(multirank_parallelsentence)
        if sort_attribute:
            multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute(sort_attribute)))
        else:
#            try:
#                multirank_parallelsentences = sorted(multirank_parallelsentences, key=lambda ps: int(ps.get_attribute("judgement_id")))
#            except:
            pass
        return DataSet(multirank_parallelsentences)



class RawPairwiseDataset(RevertablePairwiseDataset):
    """
    A data set that contains pairwise comparisons organized by human judgment, i.e. there is a separate entry for each judgment,
    even if there are more than one judgment per sentence
    @ivar replacement: Defines whether pairs are done in all combinations without replacement (replacement=False) or with replacement (replacement=True)
    @type replacement: boolean
    @ivar include_references: Defines whether references need to be included in pairs, as sentences from system "_ref". 
    Do not enable this for test-sets, as reverting this is not yet supported
    @type include_references: boolean
    """
    
    
    def __init__(self, plain_dataset = DataSet(), **kwargs):
        """
        @param plain_dataset: the simple dataset to be converted or wrapped to an analytic one. Casting of an already pairwise simple set is supported, see L{cast}
        @type plain_dataset: L{DataSet}
        @param replacement: Defines whether pairs are done in all combinations without replacement (replacement=False) or with replacement (replacement=True)
        @type replacement: boolean
        @param include_references: Defines whether references need to be included in pairs, as sentences from system "_ref". 
        Do not enable this for test-sets, as reverting this is not yet supported
        @type include_references: boolean  
        @param cast: Cast (reload) an existing pairwise set of simple DataSet as RawPairwiseDataset. No pairwise conversions are done then
        @type cast: boolean
        """
        self.pairwise_parallelsentence_sets = OrderedDict()
        pairwise_parallelsentences_per_sid = OrderedDict()
        
        cast = kwargs.setdefault("cast", None)
        self.include_references = kwargs.setdefault("include_references", False)
        self.replacement = kwargs.setdefault("replacement", False)
        
        if cast:
            self._cast(cast)
        else:
            
            #first group by sentence ID or judgment ID
            for parallelsentence in plain_dataset.get_parallelsentences():
            
                judgment_id = parallelsentence.get_compact_judgment_id()
                pairwise_parallelsentences_per_sid[judgment_id] = parallelsentence.get_pairwise_parallelsentences(replacement=self.replacement, include_references=self.include_references)
                
            
            for judgment_id, pairwiseparallelsentences in pairwise_parallelsentences_per_sid.iteritems():
            #then convert each group to a Analytic Pairwise Parallel SentenceSet
                self.pairwise_parallelsentence_sets[judgment_id] = CompactPairwiseParallelSentenceSet(pairwiseparallelsentences)
    
    
    def _cast(self, analytic_dataset=DataSet()):
        """
        Typecast a DataSet that is in fact already analytic
        """
        self.pairwise_parallelsentence_sets = OrderedDict()
        pairwise_parallelsentences_per_sid = OrderedDict()
        
        #first group by sentence ID or judgment ID
        for parallelsentence in analytic_dataset.get_parallelsentences():
        
            judgment_id = parallelsentence.get_compact_judgment_id()
            pairwiseparallelsentence = PairwiseParallelSentence(cast=parallelsentence)
            pairwise_parallelsentences_per_sid.setdefault(judgment_id, []).append(pairwiseparallelsentence)
            
        for judgment_id, pairwiseparallelsentences in pairwise_parallelsentences_per_sid.iteritems():
        #then convert each group to a Analytic Pairwise Parallel SentenceSet
            self.pairwise_parallelsentence_sets[judgment_id] = CompactPairwiseParallelSentenceSet(pairwiseparallelsentences)      
        
        
        

class AnalyticPairwiseDataset(PairwiseDataset):
    """
    A data set that contains pairwise comparisons organized by sentence id, i.e. if a sentence has multiple human judgments, 
    these will be grouped together under the sentence id  
    @ivar replacement: Defines whether pairs are done in all combinations without replacement (replacement=False) or with replacement (replacement=True)
    @type replacement: boolean
    @ivar include_references: Defines whether references need to be included in pairs, as sentences from system "_ref". 
    Do not enable this for test-sets, as reverting this is not yet supported
    @type include_references: boolean
    @ivar invert_ranks: Whether ranks should be considered the way round (highest value=best rank)
    @type invert_ranks: boolean
    """
    
    
    def __init__(self, plain_dataset = DataSet(), **kwargs):
        """
        @param plain_dataset: the simple dataset to be converted to an analytic one.
        @type plain_dataset: L{DataSet}
        @param replacement: Defines whether pairs are done in all combinations without replacement (replacement=False) or with replacement (replacement=True)
        @type replacement: boolean
        @param include_references: Defines whether references need to be included in pairs, as sentences from system "_ref". 
        Do not enable this for test-sets, as reverting this is not yet supported
        @type include_references: boolean   
        @param restrict_ranks: Filter pairs to keep only for the ones that include the given ranks. Don't filter if list empty. Before
        using this, make sure that the ranks are normalized        
        @type restrict_ranks: [int, ...] 
        @var invert_ranks: Whether ranks should be considered the way round (highest value=best rank)
        @type invert_ranks: boolean
        """
        self.pairwise_parallelsentence_sets = OrderedDict()
        pairwise_parallelsentences_per_sid = OrderedDict()
        
        self.include_references = kwargs.setdefault("include_references", False)
        self.replacement = kwargs.setdefault("replacement", True)
        self.filter_unassigned = kwargs.setdefault("filter_unassigned", False)
        self.restrict_ranks = kwargs.setdefault("restrict_ranks", [])
        self.rank_name = kwargs.setdefault("rank_name", "rank")
        self.invert_ranks = kwargs.setdefault("invert_ranks", False)
        self.rankless = kwargs.setdefault("rankless", False)
        
        #first group by sentence ID or judgment ID
        for parallelsentence in plain_dataset.get_parallelsentences():
            #get a universal sentence_id (@todo: this could be parametrized)
            sentence_id = parallelsentence.get_fileid_tuple()
            pairwise_parallelsentences_per_sid.setdefault(sentence_id, []).extend(
                                                                                  parallelsentence.get_pairwise_parallelsentences_old(
                                                                                                                                  replacement=self.replacement, 
                                                                                                                                  include_references=self.include_references,
                                                                                                                                  filter_unassigned = self.filter_unassigned,
                                                                                                                                  invert_ranks = self.invert_ranks,
                                                                                                                                  rank_name = self.rank_name,
#                                                                                                                                  restrict_ranks = self.restrict_ranks    
                                                                                                                                  rankless = self.rankless
                                                                                                                                  )
                                                                                  )
            
        for sentence_id, pairwiseparallelsentences in pairwise_parallelsentences_per_sid.iteritems():
        #then convert each group to a Analytic Pairwise Parallel SentenceSet
            self.pairwise_parallelsentence_sets[sentence_id] = AnalyticPairwiseParallelSentenceSet(
                                                                                                   pairwiseparallelsentences,
                                                                                                   rank_name = self.rank_name
                                                                                                   )
            if self.restrict_ranks: 
                self.pairwise_parallelsentence_sets[sentence_id].restrict_ranks(self.restrict_ranks)
   
    
    def restrict_ranks(self, restrict_ranks):
        """
        Modifies the current dataset by 
        """
        if self.restrict_ranks != restrict_ranks:
            sys.stderr.write("Warning: trying to filter out rank values, although this has happenned before")
        self.restrict_ranks = restrict_ranks
        for p in self.pairwise_parallelsentence_sets.itervalues:
            p.restrict_ranks(restrict_ranks)
             

        

class CompactPairwiseDataset(RevertablePairwiseDataset):
    """
    A data set that contains pairwise comparisons merged by sentence id, i.e. if a sentence has multiple human judgments, 
    these will be grouped together under the sentence id, and the overlapping pairwise judgments will be merged according
    to soft or hard rank recomposition  
    """
    def __init__(self, analytic_pairwise_dataset = AnalyticPairwiseDataset()):
        self.pairwise_parallelsentence_sets = OrderedDict()
        for sentence_id, analytic_pairwise_parallelsentence_set in analytic_pairwise_dataset.get_pairwise_parallelsentence_sets().iteritems():
            self.pairwise_parallelsentence_sets[sentence_id] = analytic_pairwise_parallelsentence_set.get_compact_pairwise_parallelsentence_set()
        


class FilteredPairwiseDataset(CompactPairwiseDataset):
    def __init__(self, analytic_pairwise_dataset = AnalyticPairwiseDataset(), threshold = 1.00):    
        self.pairwise_parallelsentence_sets = OrderedDict()
        for sentence_id, analytic_pairwise_parallelsentence_set in analytic_pairwise_dataset.get_pairwise_parallelsentence_sets().iteritems():
            self.pairwise_parallelsentence_sets[sentence_id] = analytic_pairwise_parallelsentence_set.get_filtered_pairwise_parallelsentence_set(threshold)
            

from dataprocessor.ce.cejcml import CEJcmlReader
from dataprocessor.sax.saxps2jcml import IncrementalJcml

def pairwise_ondisk(plain_filename, pairwise_filename, read_method=CEJcmlReader, write_method=IncrementalJcml, **kwargs):
        #self.read_method = read_method
        #self.plain_filename = plain_filename
        #self.pairwise_filename = pairwise_filename
        plain_dataset = read_method(plain_filename, all_general=True, all_target=True)
        pairwise_dataset = write_method(pairwise_filename) 
        
        for parallelsentence in plain_dataset.get_parallelsentences():
            pairwise_parallelsentences = parallelsentence.get_pairwise_parallelsentences(**kwargs)
            for pairwise_parallelsentence in pairwise_parallelsentences:
                pairwise_dataset.add_parallelsentence(pairwise_parallelsentence)
        pairwise_dataset.close()
        
        #self.pairwise_filename = pairwise_filename 
    
#    def get_parallelsentences(self):
#        pairwise_dataset = self.read_method(self.pairwise_filename)
#        for parallelsentence in pairwise_dataset.get_parallelsentences():
#            yield parallelsentence
    
        
        
            


        



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
#        ranking_entries = OrderedDict()
#        for judgement_id, parallelsentence in dataset.get_parallelsentences_with_judgment_ids().iteritems():
#            #get the pairwise representation of the current ranking judgment 
#            pairwise_parallel_sentences = parallelsentence.get_pairwise_parallelsentence_set()
#            #add the pair into the dictionary mapped to the unique judgment id
#            ranking_entries[judgement_id] = pairwise_parallel_sentences
#        return ranking_entries
    
#    def get_ranking_entry(self, judgement_id):
#        return self.pairwise_parallelsentence_set[judgement_id]
    
#    def get_pairs_per_sentence_id(self):
#        ps_sid = OrderedDict()
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
        
        
        
    
    
            
            
            
        


        
