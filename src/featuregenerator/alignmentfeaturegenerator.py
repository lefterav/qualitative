'''
Created on 17 Sept 2011

@author: Eleftherios Avramidis based on code from Maja Popovic, David Vilar
'''

import math
from featuregenerator import FeatureGenerator
from nltk.align import AlignedSent
from operator import itemgetter
import itertools




class OldTokenAlignment:
    """
    Represents one source word aligned with its target match
    @ivar prob: Match probability
    @type prob: float
    @ivar source_id: Sentence index of the source token
    @type source_id: int
    @ivar source_token: The text of the source token
    @type source_token: str
    @ivar target_id: Sentence index of the target token
    @type target_id: int
    @ivar target_token: The text of the target token
    @type target_token: str
    """
    def __init__(self, source_id, source_token, target_id, target_token, prob=None):
        self.prob = prob
        self.source_id = source_id
        self.source_token = source_token
        self.target_id = target_id
        self.target_token = target_token
        
    def __str__(self):
        return "{}-{}".format(self.source_id, self.target_id)

class SimpleTokenAlignment(TokenAlignment):
    def __init__(self, string):
        self.source_id, self.target_id = string.strip().split("-")



class AlignmentFeatureGenerator(FeatureGenerator):
    '''
    Provides features generation from IBM Model 1 (See Popovic et. al 2011)
    '''


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
        
    def get_features_tgt(self, simplesentence, parallelsentence):
        source_line = parallelsentence.get_source().get_string()
        target_line = simplesentence.get_string()
        score = self.get_score(source_line, target_line)
        attributes = {'ibm1-score' : "%.4f" % score,
                      'ibm1-alignment' : str(self.get_string_alignment(source_line, target_line))
                      }
        return attributes
    
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
    
    
    
    
    


    def get_string_alignment(self, sourcestring, targetstring):
        sourcetokens = sourcestring.split()
        targettokens = targetstring.split()
        
        alignment = SentenceAlignment()
        
        for sourcetoken in sourcetokens:
            tokenalignments = []
            for targettoken in targettokens:
                try:
                    probability = self.lex[sourcetoken, targettoken]
                except KeyError:
                    continue
                tokenalignment = TokenAlignment(targettoken, probability)
                tokenalignments.append(tokenalignment)
            
            alignment.add(tokenalignments)
                    
                
                
            
            
        

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

from collections import defaultdict


class SentenceAlignment(list):
    def __init__(self):
        self.sourcealignments = defaultdict(list)
        self.targetalignment = {}
    
    def add(self, sourcetoken, tokenalignments):
        for tokenalignment in sorted(tokenalignments, reverse=True):
            targettoken = tokenalignment.targettoken
            try:
                targettoken = self.targetalignment[sourcetoken]
                continue
            except KeyError:    
                self.targetalignment[targettoken] = sourcetoken
                self.sourcealignments[sourcetoken].append(targettoken)
     
        
    def get_alignment_string(self):
        alignmentstrings = []
        for sourcetoken, targettokens in self.sourcealignments.iteritems():
            
            for targettoken in targettokens:
                tokenalignmentstring = "{}-{}".format(sourcetoken, targettoken)
                alignmentstrings.append(tokenalignmentstring)
        return " ".join(alignmentstrings)
        
        #check that no target word has a double source token    
                
    
    
            
if __name__ == "__main__":
    alignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.6.e2f"
    aligner = AlignmentFeatureGenerator(alignmentfile)
    print aligner.get_string_alignment("das ist eine gute Idee , er hat gesagt", "he said that this is a good idea")
    print aligner.get_string_alignment("er hat einen Wiederspruch und eine Erklärung gemacht", "he made an appeal and a declaration")
    
    
    
    
