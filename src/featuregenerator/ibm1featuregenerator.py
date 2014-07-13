'''
Created on 17 Sept 2011

@author: Eleftherios Avramidis based on code from Maja Popovic, David Vilar
'''

import sys
import gzip
import math
from featuregenerator import FeatureGenerator

class Ibm1FeatureGenerator(FeatureGenerator):
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
            self.lex[lexs[0]+" "+lexs[1]]=lexs[2]
            lexs = lexline.split()
            lexline = lextxt.readline()
        
        
    def get_features_tgt(self, simplesentence, parallelsentence):
        sline = parallelsentence.get_source().get_string()
        tline = simplesentence.get_string()
        ibm1score = self.get_ibm1score(sline, tline)
        attributes = {'ibm1' : "%.4f" % ibm1score}
        return attributes
    
    
    def get_ibm1score(self, sline, tline): 
        
        swords = sline.split()
        twords = tline.split()
        lex = self.lex
        #tsScore = 1.0
        #logtsScore = 0.0
    
        logtsScore = -len(twords)*math.log10(1+len(swords))
    
        for tword in twords:
            nullpair = "NULL "+tword
            if lex.has_key(nullpair):
                sScore = float(lex[nullpair])
            else:
                sScore = 0.0
            for sword in swords:
                wordpair = sword+" "+tword
                if lex.has_key(wordpair):
                    sScore += float(lex[wordpair])
    
            #tsScore *= sScore
            if sScore==0:
                logtsScore += -10.0
            else:
                logtsScore += math.log10(sScore)
        
        return logtsScore
    
    