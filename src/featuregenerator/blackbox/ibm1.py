# -*- coding: UTF-8 -*-
'''
Loads IBM1 lexicon models and provides word-level probabilities and alignments
Created on 17 Sept 2011, updated 09 August 2014

@author: Eleftherios Avramidis including code from Maja Popovic, David Vilar
'''

import math
import logging
from collections import defaultdict
from featuregenerator import FeatureGenerator
from featuregenerator.blackbox.lm.quartiles import NgramManager

class Ibm1FeatureGenerator(FeatureGenerator):
    '''
    Provides features generation from IBM Model 1 (See Popovic et. al 2011) and basic source-to-target alignment
    @ivar sourcelexicon: object containing IBM-1 word-level lexical probabilities for translating source-to-target
    @type sourcelexicon: Lexicon
    @ivar targetlexicon: object containing IBM-1 word-level lexical probabilities for translating source-to-target
    @type targetlexicon: Lexicon
    @ivar source_language: the language code of the source language
    @type source_language: str
    @ivar target_language: the language code of the target language
    @type target_language: str

    '''
    
    feature_names = ["ibm1-score", 'ibm1-alignment', 'ibm1-score-inv', 'ibm1-alignment-inv', 'ibm1-alignment-joined', 'imb1-alignment-joined']
    
    feature_pattens = ["ibm1-ratio\-.*", "ibm1-wratio\-.*"]
    is_bilingual = True
    
    def __init__(self, model, inverted_model, thresholds=[0.2, 0.01], 
                 source_language=None, target_language=None,
                 ngram_counts_filename=None,
                 **kwargs):
        """
        Initialize an instance of a feature generator able to generate IBM-1 features and multilingual string alignments
        @param model: table with IBM-1 word-level lexical probabilities for translating source-to-target
        @type model: str
        @param inverted_model: table with IBM-1 word-level lexical probabilities for translating source-to-target
        @type inverted_model: str
        @param source_language: the language code of the source language
        @type source_language: str
        @param target_language: the language code of the target language
        @type target_language: str
        """        
        logging.info("Loading source side IBM1 model...")
        self.sourcelexicon = Lexicon(model)
        logging.info("Done. \nLoading target side IBM1 model...")
        self.targetlexicon = Lexicon(inverted_model)
        # load the ngram counts manager if its filename is provided
        if ngram_counts_filename is not None:
            logging.info("Done. \nLoading source-side corpus frequencies...")
            self.ngram_manager = NgramManager(ngram_counts_filename, 
                                              max_ngram_order=1)
        logging.info("Done.")

        self.source_language = source_language
        self.target_language = target_language
        self.thresholds = thresholds
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        source_line = parallelsentence.get_source().get_string()
        target_line = simplesentence.get_string()
        return self.get_features_strings(source_line, target_line)
    
    def get_features_strings(self, source_line, target_line):
        
        source_alignment = self.sourcelexicon.get_alignment(source_line, target_line)
        target_alignment = self.targetlexicon.get_alignment(target_line, source_line)
        source_length = len(source_line.strip().split())

        source_alignment_string = source_alignment.get_alignment_string()
        target_alignment_string = target_alignment.get_alignment_string_inv()
        joined_alignment_string = self.join_alignments(source_alignment_string, target_alignment_string)

        #translations per source word
        attributes_translation_ratio = self._get_translations_ratio(source_alignment, self.thresholds, source_length)
        
        attributes = {
                      'ibm1-score' : "%.4f" % self.sourcelexicon.get_score(source_line, target_line),
                      'ibm1-alignment' : " ".join(source_alignment_string),
                      'ibm1-score-inv' : "%.4f" % self.targetlexicon.get_score(target_line, source_line),
                      'ibm1-alignment-inv' : " ".join(target_alignment_string),
                      'ibm1-alignment-joined' : " ".join(joined_alignment_string),
                      'imb1-alignment-joined' : " ".join(joined_alignment_string)
                      }
        attributes.update(attributes_translation_ratio)

        return attributes

    def _get_translations_ratio(self, alignment, thresholds, source_length):
        """
        Average number of translations per source word, as given by IBM-1 
        table thresholded so that prob(t|s) > threshold
        """
        count = 0
        weighed_count = 0
        att = {}
        for threshold in thresholds:
            for source_item, tokenalignments in alignment.sourcealignment_probs.iteritems():
                item_count = len([t for t in tokenalignments if t.probability>threshold])
                count += item_count
                
                # average number of translations per source word in the sentence 
                # (as given by IBM 1 table thresholded such that prob(t|s) > threshold) 
                # weighted by the inverse frequency of each word in the source corpus
                item_frequency = self.ngram_manager.get_frequency(source_item)
                weighed_item_count = 1.0 * item_count * item_frequency
                weighed_count += weighed_item_count
                 
            try:
                ibm_ratio = 1.00 * count / len(alignment.sourcealignment_probs.keys())
                att['ibm1-ratio-{}'.format(threshold).replace(".","")] = ibm_ratio
                
                ibm_wratio = 1.00 * weighed_count / source_length
                att['ibm1-wratio-{}'.format(threshold).replace(".","")] = ibm_wratio
            except ZeroDivisionError:
                att['ibm1-ratio-{}'.format(threshold).replace(".","")] = 0
                att['imb1-ratio-failed'] = 1
                logging.warning("Cannot calculate ibm1 ratio because of empty alignment: {} ".format(alignment))

        return att       

    
    def join_alignments(self, sourcealignment, targetalignment):
        """
        Join the alignments of the two directions
        @param sourcealignment: the source-to-target alignment in a space separated format like "1-1 2-2" etc
        @type sourcealignment: [str, ...]
        @param targetalignment: the source-to-target alignment in a space separated format like "1-1 2-2" etc
        @type targetalignment: [str, ...]
        @return: alignment of the two directions joined together
        @rtype: [str, ...]
        """
        joined_alignment = set(sourcealignment)
        joined_alignment.update(targetalignment)
        return sorted(list(joined_alignment))
    
class Lexicon:
    """
    Object that wraps the functionality of a probabilistic word-level lexicon as produced for IBM model 1
    @ivar lex: A python dictionary that contains the probabilistic lexicon in memory
    @type lex: dict
    """

    def __init__(self, lexicon):
        '''
        Load the lexicon into the memory
        @param lexicon: points to the model of the lexicon to be loaded
        @type lexicon_filenam: str
        '''
        lextxt = open(lexicon, 'r')
        self.lex = {}

        lexline = lextxt.readline()
        lexs = lexline.split()
        
        while lexline:
            self.lex[lexs[0], lexs[1]]=float(lexs[2])
            lexs = lexline.split()
            lexline = lextxt.readline()    
    
    def get_score(self, sline, tline):
        '''
        Get the IBM-1 score for an entire sentence string to its translation
        @param sline: source sentence string
        @type sline: str
        @param tline: target sentence string
        @type tline: str
        @return: the overall IBM-1 score of the sentence
        @rtype: float
        ''' 
        swords = sline.split()
        twords = tline.split()
        lex = self.lex
        #tsScore = 1.0
        #logtsScore = 0.0
    
        logtsScore = -len(twords)*math.log10(1+len(swords))
    
        for tword in twords:
            null = "NULL"
            try:
                sScore = float(lex[null, tword])
            except KeyError:
                sScore = 0.0
            for sword in swords:
                try:
                    sScore += float(lex[sword, tword])
                except KeyError:
                    pass
    
            #tsScore *= sScore
            if sScore==0:
                logtsScore += -10.0
            else:
                logtsScore += math.log10(sScore)
        
        return logtsScore

    def calculate_alignment(self, sourcestring, targetstring):
        '''
        Produce the token alignments and push them into a sentence alignment object
        @param sourcestring: the tokenized source sentence string
        @type sourcestring: str
        @param targetstring: the tokenized target sentence string
        @type targetstring: str
        @return: The produced alignment object that contains all token alignments
        @rtype: SentenceAlignment
        '''
        sourcetokens = [Token(t,i) for i, t in enumerate(sourcestring.split())]
        targettokens = [Token(t,i) for i, t in enumerate(targetstring.split())]
        
        alignment = SentenceAlignment()
        
        #The sentence alignment is populated in a two-pass process.
        #First pass adds the most probable token alignment when both source and target token 
        #hasn't been aligned before 
        
        for sourcetoken in sourcetokens:
            tokenalignments = []
            for targettoken in targettokens:
                try:
                    probability = self.lex[sourcetoken.string, targettoken.string]
                except KeyError:
                    continue
                tokenalignment = TokenAlignment(targettoken, probability)
                tokenalignments.append(tokenalignment)
            alignment.add(sourcetoken, tokenalignments)
        
        #Second pass adds the most probable token alignment when even though a source 
        #token may have been aligned before
        
        for sourcetoken in sourcetokens:
            tokenalignments = []
            for targettoken in targettokens:
                try:
                    probability = self.lex[sourcetoken.string, targettoken.string]
                except KeyError:
                    continue
                tokenalignment = TokenAlignment(targettoken, probability)
                tokenalignments.append(tokenalignment)
            alignment.add_gaps(sourcetoken, tokenalignments) 
        
        #Finally, add alignment for unstranslated tokens or tokens that are exactly
        #the same on both sides
        
        for sourcetoken in sourcetokens:
            for targettoken in targettokens:
                if sourcetoken.string == targettoken.string:
                    alignment.add(sourcetoken, [TokenAlignment(targettoken, None)])
        return alignment
    
    def get_alignment(self, sourcestring, targetstring):
        '''
        Return the word-level alignment string for source to target
        @param sourcestring: the tokenized source sentence string
        @type sourcestring: str
        @param targetstring: the tokenized target sentence string
        @type targetstring: str
        @return: the string of the source-to-target alignment
        @rtype: str
        '''
        alignment = self.calculate_alignment(sourcestring, targetstring)
        return alignment           
            
    def get_alignment_inv(self, targetstring, sourcestring):
        '''
        Return the word-level alignment string for target to source, inverted as seen by the source
        @param targetstring: the tokenized target sentence string
        @type targetstring: str
        @param sourcestring: the tokenized source sentence string
        @type sourcestring: str
        @return: the string of the the alignment
        @rtype: str
        '''
        alignment = self.calculate_alignment(sourcestring, targetstring)
        return alignment              


class Token:
    '''
    Object that wraps the required variables for a token in a word alignment
    @ivar string: the string (text) of the token
    @param string: str
    @ivar index: the position of the token in the alignment
    @param index: int
    '''
    def __init__(self, string, index):
        self.string = string
        self.index = index


class TokenAlignment:
    '''
    Object that wraps the required information for an aligned target token in a word alignment
    @param targettoken: The aligned target token
    @type targettoken: Token
    @param probability: The probability of the target token alignment
    @type probability: float

    '''
    def __init__(self, targettoken, probability=None):
        self.targettoken = targettoken
        self.probability = probability
        
    def __lt__(self, other):
        return self.probability < other.probability
 
    def __str__(self):
        return "{} [{}]".format(self.targettoken, self.probability)


class SentenceAlignment(list):
    '''
    Object that wraps the necessary information and functionality for the IBM-1 alignment between the words of a 
    source and a translated sentence.
    @ivar sourcealignment: the target word alignments for each source token
    @type sourcealignment: {Token: [Token, ...], ...}
    @param targetalignment: the source work alignments for each target token
    @type targetalignment: {Token: [Token, ...], ...}
    '''
    def __init__(self):
        '''
        Initialize the sentence alignment object
        @param sourcealignment: the target word alignments for each source token
        @type sourcealignment: {Token: [Token, ...], ...}
        @param targetalignment: the source work alignments for each target token
        @type targetalignment: {Token: [Token, ...], ...}
        '''
        self.sourcealignment = defaultdict(list)
        self.sourcealignment_probs = defaultdict(list)
        self.targetalignment = {}
    
    def add(self, sourcetoken, tokenalignments):
        '''
        Get a source token and the possible aligned target tokens and 
        add the ones with the highest probability in place into the sentence alignment object,
        if neither source or target words have been previously aligned
        @param sourcetoken: the source token object
        @type sourcetoken: Token 
        @param targetalignments: the target token alignment
        @type targetalignments: TokenAlignment
        '''
        for tokenalignment in sorted(tokenalignments, reverse=True):
            targettoken = tokenalignment.targettoken
            if targettoken not in self.targetalignment and sourcetoken not in self.sourcealignment:
                self.targetalignment[targettoken] = sourcetoken
                self.sourcealignment[sourcetoken].append(targettoken)
                self.sourcealignment_probs[sourcetoken].append(tokenalignment)
    
    def add_gaps(self, sourcetoken, tokenalignments):
        '''
        Get a source token and the possible aligned target tokens and 
        add the ones with the highest probability in place into the sentence alignment object,
        even if source words have been previously aligned
        @param sourcetoken: the source token object
        @type sourcetoken: Token 
        @param targetalignments: the target token alignment
        @type targetalignments: TokenAlignment
        '''
        for tokenalignment in sorted(tokenalignments, reverse=True):
            targettoken = tokenalignment.targettoken
            if targettoken not in self.targetalignment:
                self.targetalignment[targettoken] = sourcetoken
                self.sourcealignment[sourcetoken].append(targettoken)
                self.sourcealignment_probs[sourcetoken].append(tokenalignment)
        
    def get_alignment_string(self):
        '''
        Return a list of aligned tokens, each alignment is a string with digits separated by a hyphen 
        e.g. ['1-2', '2-1' ...]
        @return: alignmentstrings
        @rtype: [str, str, ...]
        '''
        alignmentstrings = []
        for sourcetoken, targettokens in sorted(self.sourcealignment.items(), key=lambda alignment: alignment[0].index) :
            
            for targettoken in targettokens:
                tokenalignmentstring = "{}-{}".format(sourcetoken.index, targettoken.index)
                alignmentstrings.append(tokenalignmentstring)
        return alignmentstrings

    def get_alignment_string_inv(self):
        '''
        Return a list of inverted aligned tokens, each alignment is a string with digits separated by a hyphen 
        e.g. ['1-2', '2-1' ...]
        '''
        alignmentstrings = []
        for sourcetoken, targettokens in sorted(self.sourcealignment.items(), key=lambda alignment: alignment[0].index) :
            
            for targettoken in targettokens:
                tokenalignmentstring = "{}-{}".format(targettoken.index, sourcetoken.index)
                alignmentstrings.append(tokenalignmentstring)
        return alignmentstrings             
    
    
            
if __name__ == "__main__":
    srcalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.e2f"
    tgtalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.f2e"
    aligner = Ibm1FeatureGenerator(srcalignmentfile, tgtalignmentfile)
    print aligner.get_features_strings("das ist eine gute Idee , er hat gesagt", "he said that this is a good idea")
    print aligner.get_features_strings("er hat einen Wiederspruch und eine Erklärung gemacht", "he made an appeal and a declaration")
    
    
    
    
