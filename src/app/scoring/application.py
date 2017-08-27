'''
Created on Aug 17, 2017

@author: lefterav
'''
from featuregenerator.blackbox.counts import PunctuationFeatureGenerator,\
    LengthFeatureGenerator
from featuregenerator.blackbox.lm.ken import KenLMFeatureGenerator
from featuregenerator.blackbox.ibm1 import Ibm1FeatureGenerator
from featuregenerator.blackbox.lm.quartiles import NgramFrequencyFeatureGenerator
from featuregenerator.preprocessor import Normalizer, Tokenizer, Truecaser
from featuregenerator import FeatureGeneratorManager


class Baseline(object):
    '''
    Class that encapsulates the basic characteristics of a baseline scoring model,
    including a the preprocessors, a list of feature names and feature generators, 
    a scaler and the quality estimation model
    '''

    def __init__(self, 
                 source_language,
                 target_language,
                 config,
                 gateway):
    
                #ibm1_model,
                #ibm1_inverted_model,
                #source_lm,
                #target_lm,
                #ngram_counts_filename,
                #source_truecaser_model,
                #target_truecaser_model
                #):
        '''
        Initialize a new baseline model
        '''
        #=======================================================================
        # number of tokens in the source sentence
        # number of tokens in the target sentence
        # average source token length
        # LM probability of source sentence
        # LM probability of target sentence
        # number of occurrences of the target word within the target hypothesis (averaged for all words in the hypothesis - type/token ratio)
        # average number of translations per source word in the sentence (as given by IBM 1 table thresholded such that prob(t|s) > 0.2)
        # average number of translations per source word in the sentence (as given by IBM 1 table thresholded such that prob(t|s) > 0.01) 
        #    weighted by the inverse frequency of each word in the source corpus
        # percentage of unigrams in quartile 1 of frequency (lower frequency words) in a corpus of the source language (SMT training corpus)
        # percentage of unigrams in quartile 4 of frequency (higher frequency words) in a corpus of the source language
        # percentage of bigrams in quartile 1 of frequency of source words in a corpus of the source language
        # percentage of bigrams in quartile 4 of frequency of source words in a corpus of the source language
        # percentage of trigrams in quartile 1 of frequency of source words in a corpus of the source language
        # percentage of trigrams in quartile 4 of frequency of source words in a corpus of the source language
        # percentage of unigrams in the source sentence seen in a corpus (SMT training corpus)
        # number of punctuation marks in the source sentence
        # number of punctuation marks in the target sentence
        #=======================================================================
        
        # feature names of qualitative that correspond to the quest features above
        featureset = ['src_l_tokens',
                      'tgt-1_tokens',
                      'src_l_avgchars',
                      'src_lmprob',
                      'tgt-1_lmprob',
                      'tgt-1_l_avgoccurences',
                      'tgt-1_ibm1-ratio-02',
                      #average number of translations per source word in the sentence (as given by IBM 1 table thresholded such that prob(t|s) > 0.2) 'tgt-1_ibm1-ratio-001',
                      'src_ngrams_n1_q1',
                      # average number of translations per source word in the sentence (as given by IBM 1 table thresholded such that prob(t|s) > 0.01) weighted by the inverse frequency of each word in the source corpus 'src_ngrams_n1_q4',
                      'src_ngrams_n2_q1',
                      'src_ngrams_n2_q4',
                      'src_ngrams_n3_q1',
                      'src_ngrams_n3_q4',
                      'src_ngrams_n1',
                      'src_p_lgc',
                      'tgt-1_p_lgc']
        
        # initialize a pipeline given the required features
        fgm = FeatureGeneratorManager()
        self.pipeline = fgm.get_parallel_features_pipeline(featureset, config, source_language, target_language, gateway)
        
        # preprocessors
        source_truecaser_model = config.get("Truecaser:{}".format(source_language), "model")
        source_preprocessors = [Normalizer(language=source_language), 
                                Tokenizer(language=source_language),
                                Truecaser(language=source_language, model=source_truecaser_model)]
        
        target_truecaser_model = config.get("Truecaser:{}".format(target_language), "model")                         
        target_preprocessors = [Normalizer(language=target_language), 
                                Tokenizer(language=target_language),
                                Truecaser(language=target_language, model=target_truecaser_model)]                                
         
        self.preprocessors = []
        self.preprocessors.extend(source_preprocessors)
        self.preprocessors.extend(target_preprocessors)
        # 
        # #TODO: replace featuregenerators with autogenerated list of generators given featurenames
        # source_featuregenerators = [LengthFeatureGenerator(),
        #                             KenLMFeatureGenerator(language=source_language, model=source_lm),
        #                             NgramFrequencyFeatureGenerator(language=source_language, 
        #                                                            ngram_counts_filename=ngram_counts_filename, 
        #                                                            max_ngram_order=3),
        #                             PunctuationFeatureGenerator()]
        # 
        # target_featuregenerators = [LengthFeatureGenerator(),
        #                             KenLMFeatureGenerator(language=target_language, model=target_lm),
        #                             Ibm1FeatureGenerator(model=ibm1_model, 
        #                                                  inverted_model=ibm1_inverted_model, 
        #                                                  thresholds=[0.2, 0.01], 
        #                                                  source_language=source_language, 
        #                                                  target_language=target_language, 
        #                                                  ngram_counts_filename=ngram_counts_filename),
        #                             PunctuationFeatureGenerator()
        #                             ]
        # 
        # self.featuregenerators = []
        # self.featuregenerators.extend(source_featuregenerators)
        # self.featuregenerators.extend(target_featuregenerators)
        #=======================================================================
        
        # initialize the variable for the models
        self.model = None
        self.scaler = None        
     
    def load_regressor(self, regressor):
        '''
        Load a scikit-learn regressor model ready to produce a score
        given a list of feature values 
        @param regressor: a scikit-learn-compatible regressor
        @type regressor: sklearn.base.RegressorMixin
        
        '''
        self.model = regressor
        
    def load_scaler(self, scaler):
        '''
        Load a scikit-learn scaler in order to scale test data the
        same way as the training data
        @param scaler: a scikit-learn-compatible scaler
        @type scaler: sklearn.preprocessing.StandardScaler or similar
        '''
        self.scaler = scaler
    
    def preprocess(self, parallelsentence):
        '''
        Preprocess the parallel sentence and add annotation
        @param parallelsentence: the Parallel Sentence to be processed
        @type parallelsentence: sentence.parallelsentence.ParallelSentence
        @return: the processed parallel sentence
        @rtype: sentence.parallelsentence.ParallelSentence
        '''
        for preprocessor in self.preprocessors:
            parallelsentence = preprocessor.add_features_parallelsentence(parallelsentence)
        
        parallelsentence = self.pipeline.annotate_parallelsentence(parallelsentence)
        return parallelsentence
           
    def score(self, parallelsentence):
        '''
        Provide an estimated quality score for the given parallelsentence:
        @param parallelsentence: the parallelsentence to be scored
        @type parallelsentence: sentence.parallelsentec.ParallelSentence
        @return: a quality score for the given sentence
        @rtype: float
        '''
        parallelsentence = self.preprocess(parallelsentence)
        featurevector = parallelsentence.get_nested_featurevector(self.featurenames)
        featurevector = self.scaler.transform(featurevector)
        score = self.model.score(featurevector)
        return score