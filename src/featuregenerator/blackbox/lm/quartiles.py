'''
Created on 19 Jan 2015

@author: Eleftherios Avramidis
'''

import logging as log
import codecs
from collections import OrderedDict
#from marisa_trie import RecordTrie
from featuregenerator import LanguageFeatureGenerator 

class NgramManager(object):
    '''
    Manager of tables with n-grams counts. These are the intermediate
    tables creating in the first stage of building language models. 
    This is a python re-implementation of the  original Java n-gram 
    manager appearing in QuEst    
    @ivar cutoffs: cutoff for every n-gram order
    @type cutoffs: {C{int}: C{float}, ...}
    @ivar ngram_trie: n-gram entries 
    @type ngram_trie: {C{str}: C{float}, ...}
    '''
    
    def __init__(self, ngram_counts_filename=None, max_ngram_order=3):
        '''
        @param ngram_counts_filename: the model containing the counts
        @type ngram_counts_filename: C{str}
        @param max_ngram_order: the maximum order of n-grams in the table
        @type max_ngram_order: C{int}
        '''
        self.cutoffs = {}
        ngram_entries = []
        ngram_counts_file = codecs.open(ngram_counts_filename, 'r', 'utf-8')
        i = 0
        for line in ngram_counts_file:
            #the first n lines of the file give the cut-off frequencies
            if i < max_ngram_order and i >= 0:
                i += 1
                current_ngram_order = i
                line_items = line.split('\t')
                line_items[0] = 0
                self.cutoffs[current_ngram_order] = [int(freq) for freq in line_items]
                log.debug("Cutoff for {}-gram : {}".format(current_ngram_order, self.cutoffs[current_ngram_order]))

            else:
                ngram_string, ngram_frequency = line.split('\t')
                ngram_frequency = int(ngram_frequency)
                ngram_entries.append((ngram_string, ngram_frequency))
        log.info("Loaded {} entries".format(len(ngram_entries)))
        log.debug("Cutoffs: {}".format(self.cutoffs))
        ngram_counts_file.close()
        self.ngram_trie = dict(ngram_entries)
        #self.ngram_trie = RecordTrie("<L", ngram_entries)
    
    def get_frequency(self, ngram):
        try:
            log.debug("ngram: {}".format(ngram))
            return self.ngram_trie[ngram]
        except KeyError:
            log.warn("ngram {} not found".format(ngram))
            return 0
    
    def _get_ngrams(self, sentence_string, ngram_order):
        tokens = sentence_string.split()
        ngrams = []
        for i in range(len(tokens)-ngram_order+1):
            ngrams.append(" ".join(tokens[i:i+ngram_order]))
        return ngrams
    
    def get_ngrams_per_quartile(self, sentence_string, ngram_order, quartile):
        ngrams = self._get_ngrams(sentence_string, ngram_order)
        log.debug("Trying to retrieve cutoffs for {}-grams in q{}".format(ngram_order, quartile))

        cutoff_max = self.cutoffs[ngram_order][quartile-1]
        cutoff_min = self.cutoffs[ngram_order][quartile-2]
        log.debug("Cutoff for {}-gram quartile {}: ({}, {})".format(ngram_order, quartile, cutoff_min, cutoff_max))

        count = 0
        for ngram in ngrams:
            freq = self.get_frequency(ngram)
            if freq < cutoff_max and freq >= cutoff_min:
                count += 1         
        return 1.00 * count / len(ngrams)
    

class NgramFrequencyFeatureGenerator(LanguageFeatureGenerator):
    """
    Generator for features from n-gram counts, split into 4 frequency quartiles
    @ivar max_ngram_order: the maximum n-gram order supported by the table
    @type max_ngram_order: C{int}
    @ivar ngram_manager: the class that provides n-gram statistics
    @type ngram_manager: L{NgramManager}
    """
    
    feature_patterns = ['ngrams_n.*']
    
    def __init__(self, language=None, ngram_counts_filename=None, max_ngram_order=3):
        self.max_ngram_order = max_ngram_order
        self.ngram_manager = NgramManager(ngram_counts_filename, 
                                          max_ngram_order=max_ngram_order)
        self.language = language
    
    def get_features_string(self, sentence_string):
        features = OrderedDict()
        for ngram_order in range(1, self.max_ngram_order+1):
            for quartile in range(1, 5):
                features["ngrams_n{}_q{}".format(ngram_order, quartile)] = self.ngram_manager.get_ngrams_per_quartile(sentence_string, ngram_order, quartile)
     
        return features


if __name__ == '__main__':
    import sys
    log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
    string = "Provisional Legislature provides protection against EU ."
    ngfg = NgramFrequencyFeatureGenerator('en', sys.argv[1])
    print ngfg.get_features_string(string)
    
             
        