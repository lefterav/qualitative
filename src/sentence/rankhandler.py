'''
Created on Apr 15, 2011

@author: Eleftherios Avramidis
'''

from parallelsentence import ParallelSentence


class RankHandler(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
      

    
    def get_pairwise_from_multiclass_sentence(self, parallelsentence, allow_ties = False):
        """
        Converts a the ranked system translations of one sentence into many sentences containing one translation pair each,
        so that system output can be compared in a pairwise manner. 
        @param parallelsentence: the parallesentences than needs to be split into pairs
        @type parallelsentence: ParallelSentence
        @param allow_ties: sentences of equal performance (rank=0) will be included in the set, if this is set to True
        @type allow_ties: boolean
        @return a list of parallelsentences containing a pair of system translations and a universal rank value 
        """
        source = parallelsentence.get_source()
        translations = parallelsentence.get_translations()
        pairwise_sentences = []
    
        for system_a  in translations:
            for system_b in translations:
                if system_a == system_b:
                    continue
                rank = self.__normalize_rank__(system_a, system_b)
                if rank != 0 or allow_ties:
                    new_attributes = parallelsentence.get_attributes()
                    new_attributes["rank"] = rank 
                    pairwise_sentence = ParallelSentence(source, [system_a, system_b], None, new_attributes) 
                    pairwise_sentences.append(pairwise_sentence)
        
        for system in translations:
            #remove existing ranks
            system.del_attribute("rank")
        
        return pairwise_sentences
                
    
    def get_pairwise_from_multiclass_set(self, parallelsentences, allow_ties = False):
        pairwise_parallelsentences = []
        for parallelsentence in parallelsentences:
            pairwise_parallelsentences.extend( self.get_pairwise_from_multiclass_sentence(parallelsentence, allow_ties) )
        return pairwise_parallelsentences
            
    
    
    
    def __normalize_rank__(self, system_a, system_b):
        """
        Receives two rank scores for the two respective system outputs, compares them and returns a universal
        comparison value, namely -1 if the first system is better, +1 if the second system output is better, 
        and 0 if they are equally good. 
        """
        rank_a = system_a.get_attribute("rank")
        rank_b = system_b.get_attribute("rank")
        if rank_a < rank_b:
            rank = "-1"
        elif rank_a > rank_b:
            rank = "1"
        else:
            rank = "0"       
        return rank
        
        
        