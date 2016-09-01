# -*- coding: utf-8 -*-
"""

@author: Eleftherios Avramidis
"""
from featuregenerator import FeatureGenerator
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
                'p_special3']
  
    
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
        

class LengthFeatureGenerator(FeatureGenerator):
    """
    Class that provides a feature generator able to count the number of the tokens in the given simplesentences 
    """
    feature_names = ["l_tokens", "l_chars", "l_avgchars", "l_avgoccurences"]
            
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

        results = {"l_tokens" : str(tokens),
                "l_chars" : str(chars),
                "l_avgchars" : "{:.3}".format(avg_chars),
                "l_avgoccurences" : "{:.3}".format(avg_occurences)}

    
        return results
        
       
