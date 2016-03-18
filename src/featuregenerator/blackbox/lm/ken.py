'''
Feature generator from Language Models via KenLM. (unimplemented)
Created on Aug 25, 2014

@author: Eleftherios Avramidis
'''

from kenlm import Model
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from numpy import average, std


class KenLMFeatureGenerator(LanguageFeatureGenerator):
    '''
    Provide ngram features by querying language model via KenLM python wrapper
    '''

    def __init__(self, lang, filename):
        '''
        Load the model
        '''
        self.model = Model(filename)
        self.lang = lang
        
    def get_features_string(self, string):
        total_score = self.model.score(string, bos = True, eos = True)
        print total_score
        partial_scores = self.model.full_scores(string, bos = True, eos = True)
        ngram_lengths = []
        probs = []
        unk_count = 0
        unk_pos = []
        unk_tokens = []
        tokens = string.split()
        tokens_iter = iter(tokens)
        pos = 0
        for pos, (prob, ngram_length, wid) in enumerate(partial_scores):
            try:
                token = next(tokens_iter)
            #End of sentence score has no token
            except StopIteration:             
                token = ""
            if wid:
                unk_count += 1
                unk_pos.append(pos)
                unk_tokens.append(token)
                
            ngram_lengths.append(ngram_length)
            probs.append(prob)
            pos += 1
            
        unk_rel_pos = [(unk_pos_item * 1.00) / len(tokens) for unk_pos_item in unk_pos]
        unk_len = sum([len(token) for token in unk_tokens])
        
        if len(unk_pos) == 0:
            unk_pos = [0]
            unk_rel_pos = [0]    
        
        attributes = { 'kenlm_unk_pos_abs_avg' : average(unk_pos),
                       'kenlm_unk_pos_abs_std' : std(unk_pos),
                       'kenlm_unk_pos_abs_min' : min(unk_pos),
                       'kenlm_unk_pos_abs_max' : max(unk_pos),
                       'kenlm_unk_pos_rel_avg' : average(unk_rel_pos),
                       'kenlm_unk_pos_rel_std' : std(unk_rel_pos),
                       'kenlm_unk_pos_rel_min' : min(unk_rel_pos),
                       'kenlm_unk_pos_rel_max' : max(unk_rel_pos),
                       'kenlm_unk' : unk_count,
                       'kenlm_unk_len' : unk_len,
                       'kenlm_length_avg' : average(ngram_lengths),
                       'kenlm_length_std' : std(ngram_lengths),
                       'kenlm_length_min' : min(ngram_lengths),
                       'kenlm_length_max' : max(ngram_lengths),
                       'kenlm_probs_avg' : average(probs),
                       'kenlm_probs_std' : std(probs),
                       'kenlm_probs_min' : min(probs),
                       'kenlm_probs_max' : max(probs),                       
                       'kenlm_probs_pos_max' : probs.index(max(probs)),
                       'kenlm_probs_pos_min' : probs.index(min(probs)),
                       'kenlm_probs_low' : self._standouts(probs, -1),
                       'kenlm_probs_high' : self._standouts(probs, +1),
                       'kenlm_probs_low_pos_avg': average(self._standout_pos(probs, -1)),
                       'kenlm_probs_low_pos_std': std(self._standout_pos(probs, -1)),
                       'kenlm_prob' : total_score }
        
        return attributes

    def _standouts(self, vector, sign):
        std_value = std(vector)
        avg_value = average(vector)
        standout = 0
        
        for value in vector:
            if value*sign > (avg_value + sign*std_value):
                standout += 1
            
        return standout
    
    def _standout_pos(self, vector, sign):
        std_value = std(vector)
        avg_value = average(vector)
        standout = []
        for pos, value in enumerate(vector, start=1):
            if value*sign > (avg_value + sign*std_value):
                standout.append(pos)
            
        return standout
            
                        
            
             
        
        
