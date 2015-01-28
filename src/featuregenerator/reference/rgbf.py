'''
Created on 11 Nov 2014

@author: Elefhterios Avramidis based on code by Maja Popovic
'''

import numpy as np  
from collections import OrderedDict


def take_ngrams(line, m):
    newline = ""
    words = line.split()
    for i, word in enumerate(words):
        for j in range(1, m+1):
            if i+j <= len(words):
                for k in range(i, i+j-1):
                    newline += words[k] + "=="
                newline += words[i+j-1]
                if j < m:
                    newline += "*#"
            if j==m:
                newline += " "
   
    ngram = [[] for x in range(m)]

    newwords = newline.split()
    for newword in newwords:
        ngrams = newword.split("*#")
        for current_ngram, nw in zip(ngram, ngrams):
            if nw != "" and nw !="\n":
                current_ngram.append(nw)
    return ngram


def hyp_ref_errors(rwords, hwords):
    errorcount = 0.0
    precrec = 0.0
    missing = []

    for w in hwords:
        if w in rwords:
            j = rwords.index(w)
            del rwords[j]
        else:
            errorcount += 1
            missing.append(w)

        if len(hwords) != 0:
            precrec = 100*errorcount/len(hwords)
        else:
            if len(rwords) != 0:
                precrec = 100
            else:
                precrec = 0

    return errorcount, precrec, missing




class RgbfGenerator:
    def __init__(self, n=4, unitweights=[], ngramweights=[]):
        self.n = n
        if not ngramweights:
            ngramweights =  np.ones(n) * 1.00 / n
        self.ngramweights = ngramweights
        self.unitweights = unitweights
        pass
    
    def process_string(self, hypothesis, reference):
        return self.process_string_multiunit([hypothesis], [[reference]])
    
    def process_string_multiunit(self, hypUnits, refUnits, ngramprecrecf=True, unitprecrecf=True):
        U = len(refUnits)
        n = self.n
        
        ngramweights = self.ngramweights
        unitweights = self.unitweights
        
        if not unitweights:
            unitweights = np.ones(n) * 1.00 / U
        
        result = OrderedDict()
        
        sentRec = np.zeros(U)
        sentPrec = np.zeros(U)
        sentF = np.zeros(U)
        

        multiSentRec = 0.0
        multiSentPrec = 0.0
        multiSentF = 0.0
        
        for u, (hypUnit, refs) in enumerate(zip(hypUnits, refUnits)):

            # preparation for multiple references
    
            minNgramSentRper = np.ones(n) * 1000.0            
            minNgramSentHper = np.ones(n) * 1000.0
            bestNgramSentRperCount = np.zeros(n)
            bestNgramSentHperCount = np.zeros(n)
            bestNgramHypLength = np.zeros(n)
            bestNgramRefLength = np.zeros(n)
            bestSentRMissing = [[]]*n
            bestSentHMissing = [[]]*n
    
            hngrams = take_ngrams(hypUnit, n)
            
            for nref, ref in enumerate(refs):
    
                rngrams = take_ngrams(ref, n)
                rngrams1 = take_ngrams(ref, n)
                hngrams1 = take_ngrams(hypUnit, n)
    
    
                #############
                # precision #
                #############
    
                for kh, hypWords in enumerate(hngrams):
                    rwords1 = rngrams1[kh]
                    sentHperCount, sentHper, sentHmissing = hyp_ref_errors(rwords1, hypWords)
     
                    if sentHper < minNgramSentHper[kh]:
                        minNgramSentHper[kh] = sentHper
                        bestNgramHypLength[kh] = len(hypWords)
                        bestNgramSentHperCount[kh] = sentHperCount
                        bestSentHMissing[kh] = sentHmissing
    
            
    
                ##########
                # recall #
                ##########
    
                for kr, refWords in enumerate(rngrams):
                    hwords1 = hngrams1[kr]
                    sentRperCount, sentRper, sentRmissing = hyp_ref_errors(hwords1, refWords)
    
                    if sentRper < minNgramSentRper[kr]:
                        minNgramSentRper[kr] = sentRper
                        bestNgramRefLength[kr] = len(refWords)
                        bestNgramSentRperCount[kr] = sentRperCount
                        bestSentRMissing[kr] = sentRmissing  
            
    
            # all the references are done
    
    
            # collect ngram counts of unit "u" => total ngram counts
    
#             for i in range(n):
#                 totalUnitNgramHperCount[u][i] += bestNgramSentHperCount[i]
#                 totalUnitNgramRperCount[u][i] += bestNgramSentRperCount[i]
#                 totalUnitNgramRefLength[u][i] += bestNgramRefLength[i]
#                 totalUnitNgramHypLength[u][i] += bestNgramHypLength[i]
#     
#     
            # analysis of results: which hyp/ref n-grams do not have a match in ref/hyp 
    
#             if analyse:
#                 for ng, ngh in enumerate(bestSentHMissing):
#                     sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-ref-"+str(ng+1)+"grams: ")
#                     for wh in ngh:
#                         sys.stdout.write(wh+" ")
#                     sys.stdout.write("\n")
#     
#                 for ng, ngr in enumerate(bestSentRMissing):
#                     sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-hyp-"+str(ng+1)+"grams: ")               
#                     for wr in ngr:
#                         sys.stdout.write(wr+" ")   
#                     sys.stdout.write("\n")
#     
    
            # sentence precision, recall and F (arithmetic mean of all ngrams) for unit "u"
    
    
            sentNgramPrec = np.zeros(n)
            sentNgramRec = np.zeros(n)
            sentNgramF = np.zeros(n)


            for i in range(n):
                if bestNgramRefLength[i] != 0:
                    sentNgramRec[i] = 100 - 100*bestNgramSentRperCount[i]/bestNgramRefLength[i]
                else:
                    sentNgramRec[i] = 0
            
                if bestNgramHypLength[i] != 0:
                    sentNgramPrec[i] = 100 - 100*bestNgramSentHperCount[i]/bestNgramHypLength[i]
                else:
                    sentNgramPrec[i] = 0

                if bestNgramRefLength[i] != 0 or bestNgramHypLength[i] != 0:
                    sentNgramF[i] = 100 - 100*(bestNgramSentRperCount[i]+bestNgramSentHperCount[i])/(bestNgramRefLength[i]+bestNgramHypLength[i])
                else:
                    sentNgramF[i] = 0

                if ngramprecrecf:
                    result["u{}-{}gram-F".format(u+1, i+1)] = sentNgramF[i]
                    result["u{}-{}gram-Prec".format(u+1, i+1)] = sentNgramPrec[i]
                    result["u{}-{}gram-Rec".format(u+1, i+1)] = sentNgramRec[i]                                

                sentRec[u] += ngramweights[i] * sentNgramRec[i]
                sentPrec[u] += ngramweights[i] * sentNgramPrec[i]
                sentF[u] += ngramweights[i] * sentNgramF[i]
 
#             ==end if sent


    
            
            multiSentRec += unitweights[u] * sentRec[u]
            multiSentPrec += unitweights[u] * sentPrec[u]
            multiSentF += unitweights[u] * sentF[u]   
            
        result["rgbF"] = multiSentF
        result["rgbPrec"] = multiSentPrec
        result["rgbRec"] = multiSentRec
        #for x,y in result.iteritems():
        #    print x, "=", y
        
        return result
    


