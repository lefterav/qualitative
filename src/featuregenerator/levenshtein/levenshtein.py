'''
Calculation functions for Levenshtein distance
Created on Sep 6, 2011

@author: Eleftherios Avramidis
'''

from nltk.tokenize.punkt import PunktWordTokenizer

def levenshtein_tok(hypothesis, reference):

    hypothesis = PunktWordTokenizer().tokenize(hypothesis)
    reference = PunktWordTokenizer().tokenize(reference)    
    return levenshtein(hypothesis, reference)

def levenshtein(s1, s2):
    """
    source: wikibooks
    """

    
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]
