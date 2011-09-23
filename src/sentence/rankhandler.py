'''
Created on Apr 15, 2011

@author: Eleftherios Avramidis
'''

from parallelsentence import ParallelSentence
from dataset import DataSet

class RankHandler(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
      
    def get_multiclass_from_pairwise_set(self, parallelsentences, allow_ties = False):
        if isinstance(parallelsentences, DataSet):
            parallelsentences = parallelsentences.get_parallelsentences()
            
            
        sentences_per_judgment = {}
        #constract groups of pairwise sentences, based on their judgment id, which is unique per group
        for parallelsentence in parallelsentences:
            jid = int(parallelsentence.get_attribute("judgement_id"))
            if jid in sentences_per_judgment:
                sentences_per_judgment[jid].append(parallelsentence)
            else:
                #if this key has not been seen before, initiate a new entry
                sentences_per_judgment[jid]=[parallelsentence]
        
        new_parallelsentences = []
        
        for jid in sentences_per_judgment:
            pairwise_sentences = sentences_per_judgment[jid]
            rank_per_system = {}
            tranlsations_per_system = {}
            for pairwise_sentence in pairwise_sentences:
                rank = int(pairwise_sentence.get_attribute("rank"))
                
                #it is supposed to have only two translations
                translation1 = pairwise_sentence.get_translations()[0]
                if translation1.get_attribute("system") in rank_per_system:
                    rank_per_system[translation1.get_attribute("system")] += rank
                else:
                    rank_per_system[translation1.get_attribute("system")] = rank
                    tranlsations_per_system[translation1.get_attribute("system")] = translation1
   
                translation2 = pairwise_sentence.get_translations()[1]
                if translation2.get_attribute("system") in rank_per_system:
                    rank_per_system[translation2.get_attribute("system")] -= rank
                else:
                    rank_per_system[translation2.get_attribute("system")] = rank
                    tranlsations_per_system[translation2.get_attribute("system")] = translation2
            
            i = 0
            prev_rank = None
            translations_new_rank = []
            for system in sorted(rank_per_system, key=lambda system: rank_per_system[system]):                
                if rank_per_system[system] != prev_rank:
                    i += 1
                #print "system: %s\t%d -> %d" % (system, rank_per_system[system] , i)
                prev_rank = rank_per_system[system]
                translation = tranlsations_per_system[system]
                translation.add_attribute("rank", str(i))
                translations_new_rank.append(translation)
            
            src = pairwise_sentences[0].get_source()
            attributes = pairwise_sentences[0].get_attributes()
            del attributes["rank"]
            new_parallelsentence = ParallelSentence(src, translations_new_rank, None, attributes)
            new_parallelsentences.append(new_parallelsentence)
        return new_parallelsentences                           
                
            #print  "------------------"
                    
                
                
                
                
            
                
                
                
            
            
            
            
        
    
    def get_pairwise_from_multiclass_sentence(self, parallelsentence, judgement_id, allow_ties = False, exponential = True):
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
        systems_parsed = []
    
        for system_a  in translations:
            for system_b in translations:
                if system_a == system_b:
                    continue
                if system_b in systems_parsed and not exponential:
                    continue
                rank = self.__normalize_rank__(system_a, system_b)
                if not rank:
                    new_attributes = parallelsentence.get_attributes()
                    new_attributes["judgement_id"] = judgement_id
                    #new_attributes["orig_rank"] = new_attributes["rank"]
                    new_attributes["rank"] = "-99"
                    pairwise_sentence = ParallelSentence(source, [system_a, system_b], None, new_attributes) 
                    pairwise_sentences.append(pairwise_sentence)
                elif rank != "0" or allow_ties:
                    new_attributes = parallelsentence.get_attributes()
                    #new_attributes["orig_rank"] = new_attributes["rank"]
                    new_attributes["rank"] = rank 
                    new_attributes["judgement_id"] = judgement_id
                    pairwise_sentence = ParallelSentence(source, [system_a, system_b], None, new_attributes) 
                    pairwise_sentences.append(pairwise_sentence)
                    
        for system in translations:
            #remove existing ranks
            try:
                system.rename_attribute("rank", "orig_rank")
            except KeyError:
                print "didn't rename rank attribute"
                pass
        
        return pairwise_sentences
                
    
    def get_pairwise_from_multiclass_set(self, parallelsentences, allow_ties = False, exponential = True):
        pairwise_parallelsentences = []
        j = 0
        for parallelsentence in parallelsentences: 
            j += 1
            if "judgment_id" in parallelsentence.get_attributes():
                judgement_id = parallelsentence.get_attribute("judgment_id")
            else:
                judgement_id = str(j)
            pairwise_parallelsentences.extend( self.get_pairwise_from_multiclass_sentence(parallelsentence, judgement_id, allow_ties) )
        return pairwise_parallelsentences
            
    
    
    
    def __normalize_rank__(self, system_a, system_b):
        """
        Receives two rank scores for the two respective system outputs, compares them and returns a universal
        comparison value, namely -1 if the first system is better, +1 if the second system output is better, 
        and 0 if they are equally good. 
        """
        try:
            rank_a = system_a.get_attribute("rank")
            rank_b = system_b.get_attribute("rank")
            if rank_a < rank_b:
                rank = "-1"
            elif rank_a > rank_b:
                rank = "1"
            else:
                rank = "0"       
            return rank
        except KeyError:
            return None
        
        
        