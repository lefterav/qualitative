"""
Functions for the calculation of Word Error Rate
@author Eleftherios Avramidis based on original by Maja Popovic
"""

#!/usr/bin/env python

import sys
import gzip
from nltk.tokenize.punkt import PunktWordTokenizer


sent = False


class levNode:
    def __init__(self, rpos=0, hpos=0, error=0):
        self.rpos = rpos
        self.hpos = hpos
        self.error = error


def wer(hypWords, refs):
    """
    Basic function for returning Word Error Rate between one string and
    several references
    @param hypWords: a list of the tokens of the translation to be scored
    @type hypWords: list
    @param refs: a list of lists of tokens of the reference translations
    @type refs: list(list(str))
    @return: the Word Error Rate score
    @rtype: float
    """
    if isinstance(hypWords, str):
        hypWords = PunktWordTokenizer().tokenize(hypWords)
    if isinstance(refs, str):
        refs = PunktWordTokenizer().tokenize(refs)
    
    totalHypLength = 0.0
    totalRefLength = 0.0
    
    totalWerCount = 0.0
        
    nsent = 0
    
    
    p = (0,0)
    
    Q = {}
    Q[p] = 0
    
    B = {}
    B[p] = levNode(0, 0, 0)
        
    
    
    

    #preparation

    nsent += 1

    minWer = 1000
    bestRefLength = 0.0
    bestSentWerCount = 0.0


    maxLength=[]

    #refs = rline.split("#")

    #reading hypothesis
    
    totalHypLength += len(hypWords)


    # adjusting indices to range from 1 to len(hypWords)

    hyp = {}

    i=1

    while i <= len(hypWords):
        hyp[i] = hypWords[i-1]
        i+=1

    #reading reference(s)

    nref = 0
    
    for refWords in refs:
        

        # adjusting indices to range from 1 to len(refWords)

        i=1
        
        ref={}

        while i <= len(refWords):
            ref[i]=refWords[i-1]
            i+=1


        #maximal length (necessary for alignment)

        if len(refWords) > len(hypWords):
            maxLength.append(len(refWords))
        else:
            maxLength.append(len(hypWords))



        #Wer errors

        for nh in range(0, len(hyp)+1):
            p = (0, nh)
            Q[p]=nh
            B[p] = levNode(0, nh-1, 3)
            
            
 

        for nr in range(0, len(ref)+1):
            p = (nr, 0)
            Q[p]=nr
            B[p] = levNode(nr-1, 0, 2)
            

        p = (0, 0)
        B[p] = levNode(-1, -1, -1)
        
        p = (1, 0)
        B[p] = levNode(0, 0, 2)
        
        p = (0, 1)
        B[p] = levNode(0, 0, 3)


        # Qs and Bs

        for r in ref.keys():
            for h in hyp.keys():
                minQ = 1000
                p = (r, h)
                dp = (r-1, h)
                ip = (r, h-1)
                sp = (r-1, h-1)

                

                s = 0
                if hyp[h] != ref[r]:
                    s = 1
                else:
                    s = 0
                
                if Q[sp]+s < minQ:
                    minQ = Q[sp]+s
                    B[p] = levNode(r-1, h-1, s)
        
                if Q[dp]+1 < minQ:
                    minQ = Q[dp]+1
                    B[p] = levNode(r-1, h, 2)

                if Q[ip]+1 < minQ:
                    minQ = Q[ip]+1
                    B[p] = levNode(r, h-1, 3)

                Q[p] = minQ


                



        # backtracking
            
        sentWerCount = 0.0

        l = maxLength[nref]
 
        

        # 1) starting backtracking
        
        p = (len(refWords), len(hypWords))

        err = B[p].error


        if err == 1 or err == 2 or err == 3:
            sentWerCount+=1



        rp = B[p].rpos
        hp = B[p].hpos

        # 2) going down


        while hp >= 0 and rp >= 0:
            p1 = (rp, hp)
            err = B[p1].error

            
            if err == 1 or err == 2 or err ==3:
                sentWerCount+=1
                
            l -= 1

            hp = B[p1].hpos
            rp = B[p1].rpos
            

        
        # best sentence wer & best reference

        rLen = 0.00000001
        if len(refWords) > 0:
            rLen = len(refWords)
            
        sentWer = sentWerCount/rLen
        if sentWer < minWer:
            minWer = sentWer
            bestRefLength = len(refWords)
            bestSentWerCount = sentWerCount
            
        nref += 1

        Q.clear()
        B.clear()

        

    totalRefLength += bestRefLength

    totalWerCount += bestSentWerCount

    

    #sys.stdout.write(str(nsent)+"::Wer: "+str("%.4f" % minWer)+"\n")
    return minWer