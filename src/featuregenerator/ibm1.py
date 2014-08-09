# -*- coding: UTF-8 -*-
'''
Loads IBM1 lexicon models and provides word-level probabilities and alignments
Created on 17 Sept 2011, updated 09 August 2014

@author: Eleftherios Avramidis based on code from Maja Popovic, David Vilar
'''

import math
from featuregenerator import FeatureGenerator

class AlignmentFeatureGenerator(FeatureGenerator):
    '''
    Provides features generation from IBM Model 1 (See Popovic et. al 2011)
    '''
    def __init__(self, source_lexicon_filename, target_lexicon_filename):
        self.sourcelexicon = Lexicon(source_lexicon_filename)
        self.targetlexicon = Lexicon(target_lexicon_filename)
        
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        source_line = parallelsentence.get_source().get_string()
        target_line = simplesentence.get_string()
        return self.get_features_strings(source_line, target_line)
    
    def get_features_strings(self, source_line, target_line):
        
        source_alignment = self.sourcelexicon.get_string_alignment(source_line, target_line)
        target_alignment = self.sourcelexicon.get_string_alignment(target_line, source_line)
        joined_alignment = self.join_alignments(source_alignment, target_alignment)
        
        attributes = {
                      'ibm1-score' : "%.4f" % self.sourcelexicon.get_score(source_line, target_line),
                      'ibm1-alignment' : " ".join(source_alignment),
                      'ibm1-score-inv' : "%.4f" % self.get_score(target_line, source_line),
                      'ibm1-alignment-inv' : " ".join(target_alignment),
                      'imb1-alignment-joined' : " ".join(joined_alignment)
                      }
        return attributes
    
    def join_alignments(self, sourcealignment, targetalignment):
        joined_alignment = set(sourcealignment)
        joined_alignment = joined_alignment.union(set(targetalignment))
        return list(joined_alignment)

    
class Lexicon:

    def __init__(self, lexicon_filename):
        '''
        Load the lexicon into a dict
        '''
        lextxt = open(lexicon_filename, 'r')
        self.lex = {}

        lexline = lextxt.readline()
        lexs = lexline.split()
        
        while lexline:
            self.lex[lexs[0], lexs[1]]=float(lexs[2])
            lexs = lexline.split()
            lexline = lextxt.readline()    

    
    def get_score(self, sline, tline): 
        
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
        sourcetokens = [Token(t,i) for i, t in enumerate(sourcestring.split())]
        targettokens = [Token(t,i) for i, t in enumerate(targetstring.split())]
        
        alignment = SentenceAlignment()
        
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
        
        return alignment
    
    
    def get_alignment(self, sourcestring, targetstring):
        alignment = self.get_alignment(sourcestring, targetstring)
        return alignment.get_alignment_string()           
                
    def get_alignment_inv(self, targetstring, sourcestring):
        alignment = self.get_alignment(sourcestring, targetstring)
        return alignment.get_alignment_string_inv()              
            
        

class Token:
    def __init__(self, string, index):
        self.string = string
        self.index = index
    
class TokenAlignment:
    def __init__(self, targettoken, probability=None):
        self.targettoken = targettoken
        self.probability = probability
        
    def __lt__(self, other):
        return self.probability < other.probability
 
    def __str__(self):
        return "{} [{}]".format(self.targettoken, self.probability)

from collections import defaultdict


class SentenceAlignment(list):
    def __init__(self):
        self.sourcealignment = defaultdict(list)
        self.targetalignment = {}
    
    def add(self, sourcetoken, tokenalignments):
        for tokenalignment in sorted(tokenalignments, reverse=True):
            targettoken = tokenalignment.targettoken
            if targettoken not in self.targetalignment and sourcetoken not in self.sourcealignment:
                self.targetalignment[targettoken] = sourcetoken
                self.sourcealignment[sourcetoken].append(targettoken)
    
    def add_gaps(self, sourcetoken, tokenalignments):
        for tokenalignment in sorted(tokenalignments, reverse=True):
            targettoken = tokenalignment.targettoken
            if targettoken not in self.targetalignment:
                self.targetalignment[targettoken] = sourcetoken
                self.sourcealignment[sourcetoken].append(targettoken)
     
        
    def get_alignment_string(self):
        alignmentstrings = []
        for sourcetoken, targettokens in sorted(self.sourcealignment.items(), key=lambda alignment: alignment[0].index) :
            
            for targettoken in targettokens:
                tokenalignmentstring = "{}-{}".format(sourcetoken.index, targettoken.index)
                alignmentstrings.append(tokenalignmentstring)
        return alignmentstrings

    def get_alignment_string_inv(self):
        alignmentstrings = []
        for sourcetoken, targettokens in sorted(self.sourcealignment.items(), key=lambda alignment: alignment[0].index) :
            
            for targettoken in targettokens:
                tokenalignmentstring = "{}-{}".format(targettoken, sourcetoken)
                alignmentstrings.append(tokenalignmentstring)
        return alignmentstrings
        
        #check that no target word has a double source token    
                
    
    
            
if __name__ == "__main__":
    srcalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.e2f"
    tgtalignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.2.f2e"
    aligner = AlignmentFeatureGenerator(srcalignmentfile, tgtalignmentfile)
    print aligner.get_features_strings("das ist eine gute Idee , er hat gesagt", "he said that this is a good idea")
    print aligner.get_features_strings("er hat einen Wiederspruch und eine Erklärung gemacht", "he made an appeal and a declaration")
    
    
    
    
