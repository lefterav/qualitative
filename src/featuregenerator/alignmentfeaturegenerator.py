'''
Created on 17 Sept 2011

@author: Eleftherios Avramidis based on code from Maja Popovic, David Vilar
'''

import math
from featuregenerator import FeatureGenerator
from nltk.align import AlignedSent






class TokenAlignment:
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
            self.lex[lexs[0], lexs[1]]=lexs[2]
            lexs = lexline.split()
            lexline = lextxt.readline()    
        
    def get_features_tgt(self, simplesentence, parallelsentence):
        source_line = parallelsentence.get_source().get_string()
        target_line = simplesentence.get_string()
        score = self.get_score(source_line, target_line)
        attributes = {'giza' : "%.4f" % score,
                      #'alignment' : str(self.get_alignment_string(source_line, target_line))
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
    
    def get_alignment_string(self, source_line, target_line):
        alignment = []
        for source_id, source_token in enumerate(source_line.split(), start=0):
            tokenalignment = self.get_alignment_token(source_token, target_line)
            if tokenalignment:                
                alignment.append(tokenalignment)
        return alignment
    
    def get_alignment_token(self, source_token, target_line):
        matches = []
        for target_id, target_token in enumerate(target_line.split(), start=0):
            try:
                prob = self.lex[source_token, target_token] 
                matches.append((prob, target_id, target_token))
            except KeyError:
                pass
        try:
            match_prob, match_target_id, match_target_token = max(matches)
        except:
            return None
        return TokenAlignment(match_prob, match_target_id, match_target_token)
            
    
    
            
if __name__ == "__main__":
    alignmentfile = "/share/taraxu/systems/r2/de-en/moses/model/lex.6.e2f"
    aligner = AlignmentFeatureGenerator(alignmentfile)
    print aligner.get_alignment_string("das ist eine gute Idee , er hat gesagt", "He said that this is a good idea")
    
    
    
    
