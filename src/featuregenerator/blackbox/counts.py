"""

@author: Eleftherios Avramidis
"""
from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer


class PunctuationFeatureGenerator(FeatureGenerator):
    
    def get_features_string(self, sent_string):
        
        #punctuation marks
        punctuation_marks = {'commas': ',',
                'dots': '.',
                'questionmarks': '?',
                'questionmark_start': '',
                'exclamations': '!',
                'exclamation_start': '',
                'colons': ':',
                'semicolons': ';',
                'hyphens': '-',
                'apostrophes': "'",
                'quotes': '"',
                'openbrackets': "(",
                'closebrackets': ")",
                'special1': "؟",
                'special2': "،",
                'special3': "؛"}
    
    
        tokenlist = sent_string.split(' ')
    
        attributes = {}
        punc_totalcount = 0
        punc_legacycount = 0 #as counted by quest
        for name, character in punctuation_marks.iteritems():
            attributes["l_{}".format(name)] = tokenlist.count(character)
            punc_totalcount += attributes[name]
            if name in ["commas", "dots", "questionmarks", "questionmark_start", "exclamations", "exclamation_start", "colon", "semicolon"]:
                punc_legacycount += attributes[name]
        

class LengthFeatureGenerator(FeatureGenerator):
    """
    Class that provides a feature generator able to count the number of the tokens in the given simplesentences 
    """

            
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
        
       
