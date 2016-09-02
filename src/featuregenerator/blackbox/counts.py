# -*- coding: utf-8 -*-
"""

@author: Eleftherios Avramidis
"""
from featuregenerator import FeatureGenerator
from debian.arfile import a
import re
#from nltk.tokenize.punkt import PunktWordTokenizer

class PunctuationFeatureGenerator(FeatureGenerator):
    
    feature_names = ['p_commas', 'p_dots', 'p_questionmarks', 'p_questionmark_start',
                'p_exclamations',
                'p_exclamation_start',
                'p_colons',
                'p_semicolons',
                'p_hyphens',
                'p_apostrophes',
                'p_quotes',
                'p_openbrackets',
                'p_closebrackets',
                'p_special1',
                'p_special2',
                'p_special3',
                'p_commas_diff',
                ]
  
    
    def get_features_string(self, sent_string):
        
        #punctuation marks
        punctuation_marks = {'commas': ',',
                'dots': '.',
                'questionmarks': '?',
                'questionmark_start': u'¿',
                'exclamations': '!',
                'exclamation_start': u'¡',
                'colons': ':',
                'semicolons': ';',
                'hyphens': '-',
                'apostrophes': "'",
                'quotes': '"',
                'openbrackets': "(",
                'closebrackets': ")",
                'special1': u"؟",
                'special2': u"،",
                'special3': u"؛"}
    
    
    
        attributes = {}
        punc_totalcount = 0
        punc_legacycount = 0 #as counted by quest
        for name, character in punctuation_marks.iteritems():
            thiscount = sent_string.count(character) 
            attributes["p_{}".format(name)] = thiscount
            punc_totalcount += thiscount
            if name in ["commas", "dots", "questionmarks", "questionmark_start", "exclamations", "exclamation_start", "colon", "semicolon"]:
                punc_legacycount += thiscount
        attributes["p_all"] = punc_totalcount
        attributes["p_lgc"] = punc_legacycount
        return attributes
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        attributes = self.get_features_simplesentence(self, simplesentence, parallelsentence)
        source_attributes = self.get_features_src(parallelsentence.get_source())
        #getting only this diff, since it seems it is successful in previous experiments 
        attributes["p_commas_diff"] = source_attributes["p_commas"] - attributes['p_commas']
        return attributes 
        

class LengthFeatureGenerator(FeatureGenerator):
    """
    Class that provides a feature generator able to count the number of the tokens in the given simplesentences 
    """
    feature_names = ["l_tokens", "l_chars", "l_avgchars", "l_avgoccurences", 
                     "l_numbers", "l_non_aztokens", "l_non_aztokens_per", 
                     "l_srctokens_ratio", "l_ratio", 'l_numbers_diff_norm', "l_aztokens_ratio"]
            
    def get_features_string(self, sent_string):
        """
        Uses NLTK toolkit in order to tokenize given simplesentence and provide a feature with the number of tokens
        @param simplesentence: The SimpleSentence whose words are to be counted
        @type simplesentence: sentence.sentence.SimpleSentence
        @rtype: dict
        @return: dictionary containing lenght attribute 
        """
        sent_string = sent_string.strip()
        chars = len(sent_string)
        
        #number of occurrences of each word within the sentence (averaged for all words in the sentence - type/token ratio
        tokenlist = sent_string.split(' ')
        tokens = len(tokenlist)
        unique_tokens = set(tokenlist)
        avg_occurences = 1.000 * tokens / len(unique_tokens)
        avg_chars = 1.000 * chars / tokens
        
        numbers = len([i for i in re.findall('[\d,.]*', sent_string) if i])
        az_tokens = len([i for i in re.findall('[A-Za-z]*', a) if i])
        non_az_tokens = tokens - az_tokens
        non_az_tokens_per = non_az_tokens * 1.00 / tokens

        results = {"l_tokens" : tokens, 
                "l_chars" : chars,
                "l_avgchars" : "{:.3}".format(avg_chars),
                "l_avgoccurences" : "{:.3}".format(avg_occurences),
                "l_numbers" : numbers,    
                "l_aztokens" : az_tokens,
                "l_non_aztokens" : non_az_tokens,            
                "l_non_aztokens_per" : non_az_tokens_per,
                }

    
        return results
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        attributes = self.get_features_simplesentence(simplesentence, parallelsentence)
        source_attributes = self.get_features_src(parallelsentence.get_source())
        #manually adding supplements for sucessful quest features        
        attributes["l_srctokens_ratio"] = (1.00 * source_attributes['l_tokens']) / attributes['l_tokens'] 
        attributes["l_tokens_ratio"] = attributes['l_tokens'] / (1.00 * source_attributes['l_tokens'])
        attributes["l_numbers_diff_norm"] = (source_attributes['l_numbers'] - attributes['l_numbers']) * 1.00 / source_attributes['l_tokens']  
        attributes["l_aztokens_ratio"] = source_attributes['l_aztokens'] / (1.00 * attributes['l_aztokens'])
        return attributes()
       
