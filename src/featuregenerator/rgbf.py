'''
Encapsulates functionality of rgbF metric by Maja Popovic for calculating F-score against reference
Created on 24 Sep 2014

@author: Maja Popovic, Eleftherios Avramidis
'''



#!/usr/bin/env python

# Copyright 2012 Maja Popovic

import sys
import gzip

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
                    newline += "#"
            if j==m:
                newline += " "
   
    ngram = [[] for x in range(m)]

    newwords = newline.split()
    for newword in newwords:
        ngrams = newword.split("#")
        for nnw, nw in enumerate(ngrams):
            if nw != "" and nw !="\n":
                ngram[nnw].append(nw)

    return ngram


def hyp_ref_errors(rwords, hwords):
    errorcount = 0.0
    precrec = 0.0

    for w in hwords:
        if w in rwords:
            j = rwords.index(w)
            del rwords[j]
        else:
            errorcount += 1

        if len(hwords) != 0:
            precrec = 100*errorcount/len(hwords)
        else:
            if len(rwords) != 0:
                precrec = 100
            else:
                precrec = 0

    return errorcount, precrec


class RgbfFeatureGenerator(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        


sent = False
unitprecrecf = False
ngramprecrecf = False
prec = False
rec = False
nweight = False
uweight = False
nweights = []
uweights = []

n = 4

args = sys.argv
if len(args) < 5:
    print("\nrgbF.py \t\t -R, --ref   reference \n \t\t\t -H, --hyp   hypothesis \n\noptional inputs: \t -n,  --ngram     ngram order (default = 4) \n \t\t\t -uw, --uweight   unit weights (default = 1/U, U = number of different units) \n \t\t\t -nw, --nweight   ngram weights (default = 1/n) \n\noptional outputs: \t -p, --prec   show precisions \n  \t\t\t -r, --rec    show recalls \n \t\t\t -u, --unit   show separate unit scores \n \t\t\t -g, --gram   show separate ngram scores \n \t\t\t -s, --sent   show sentence level scores \n")
    sys.exit()
for arg in args:
    if arg == "-R" or arg == "--ref":
        rtext = args[args.index(arg)+1]
    elif arg == "-H" or arg == "--hyp":
        htext = args[args.index(arg)+1]
    elif arg == "-s" or arg == "--sent":
        sent = True
    elif arg == "--ngram" or arg == "-n":
        n = int(args[args.index(arg)+1])
    elif arg == "-uw" or arg == "--uweight":
        uweight = True
        uweights = (args[args.index(arg)+1]).split("-")
    elif arg == "-nw" or arg == "--nweight":
        nweight = True
        nweights = (args[args.index(arg)+1]).split("-") 
    elif arg == "-u" or arg == "--unit":
        unitprecrecf = True
    elif arg == "-g" or arg == "--gram":
        ngramprecrecf = True
    elif arg == "-r" or arg == "--rec":
        rec = True
    elif arg == "-p" or arg == "--prec":
        prec = True

rtxt = open(rtext, 'r')
htxt = open(htext, 'r')

hline = htxt.readline()
rline = rtxt.readline()

# separating different units (words, POS, etc)

hypUnits = hline.split("++")
refUnits = rline.split("++")
U = len(refUnits)

totalUnitNgramRperCount = [[0.0 for x in range(n)] for y in range(U)]
totalUnitNgramHperCount = [[0.0 for x in range(n)] for y in range(U)]
totalUnitNgramHypLength = [[0.0 for x in range(n)] for y in range(U)]
totalUnitNgramRefLength = [[0.0 for x in range(n)] for y in range(U)]

nsent = 0

ngramweights = []
unitweights = []

if not(nweight):
    ngramweights = [1/float(n) for x in range(n)]
else:
    if len(nweights) != n:
        print("error: ngram weights length!")
        sys.exit()
    total = 0.0
    for i in range(len(nweights)):
        total += float(nweights[i])
    for i in range(len(nweights)):
        ngramweights.append(float(nweights[i])/total)

if not(uweight):
    unitweights = [1/float(U) for y in range(U)]
else:
    if len(uweights) != U:
        print("error: unit weights length!")
        sys.exit()   
    total = 0.0
    for i in range(len(uweights)):
        total += float(uweights[i])
    for i in range(len(uweights)):
        unitweights.append(float(uweights[i])/total) 


while (hline and rline):

    nsent += 1


    sentRec = [0.0 for y in range(U)]
    sentPrec = [0.0 for y in range(U)]
    sentF = [0.0 for y in range(U)]


    multiSentRec = 0.0
    multiSentPrec = 0.0
    multiSentF = 0.0

    # going through all units

    for u in range(U):

        # preparation for multiple references

        minNgramSentRper = [1000.0 for x in range(n)]
        minNgramSentHper = [1000.0 for x in range(n)]
        bestNgramSentRperCount = [0.0 for x in range(n)]
        bestNgramSentHperCount = [0.0 for x in range(n)]
        bestNgramHypLength = [0.0 for x in range(n)]
        bestNgramRefLength = [0.0 for x in range(n)]

        hngrams = take_ngrams(hypUnits[u], n)


        # going through multiple references

        refs = refUnits[u].split("#")

        nref = 0

        for ref in refs:
            nref += 1

            rngrams = take_ngrams(ref, n)
            rngrams1 = take_ngrams(ref, n)
            hngrams1 = take_ngrams(hypUnits[u], n)


            #############
            # precision #
            #############

            for kh, hypWords in enumerate(hngrams):
                rwords1 = rngrams1[kh]
                sentHperCount, sentHper = hyp_ref_errors(rwords1, hypWords)
 
                if sentHper < minNgramSentHper[kh]:
                    minNgramSentHper[kh] = sentHper
                    bestNgramHypLength[kh] = len(hypWords)
                    bestNgramSentHperCount[kh] = sentHperCount

        

            ##########
            # recall #
            ##########

            for kr, refWords in enumerate(rngrams):
                hwords1 = hngrams1[kr]
                sentRperCount, sentRper = hyp_ref_errors(hwords1, refWords)

                if sentRper < minNgramSentRper[kr]:
                    minNgramSentRper[kr] = sentRper
                    bestNgramRefLength[kr] = len(refWords)
                    bestNgramSentRperCount[kr] = sentRperCount
   
        

        # all the references are done


        # collect ngram counts of unit "u" => total ngram counts

        for i in range(n):
            totalUnitNgramHperCount[u][i] += bestNgramSentHperCount[i]
            totalUnitNgramRperCount[u][i] += bestNgramSentRperCount[i]
            totalUnitNgramRefLength[u][i] += bestNgramRefLength[i]
            totalUnitNgramHypLength[u][i] += bestNgramHypLength[i]


        # sentence precision, recall and F (arithmetic mean of all ngrams) for unit "u"
    
        if sent:
            sentNgramPrec = [0.0 for x in range(n)]
            sentNgramRec = [0.0 for x in range(n)]
            sentNgramF = [0.0 for x in range(n)]


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
                    sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-"+str(i+1)+"gram-F     "+str("%.4f" % sentNgramF[i])+"\n")
                    if prec:
                        sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-"+str(i+1)+"gram-Prec  "+str("%.4f" % sentNgramPrec[i])+"\n")
                    if rec:
                        sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-"+str(i+1)+"gram-Rec   "+str("%.4f" % sentNgramRec[i])+"\n")

                                   

                sentRec[u] += ngramweights[i]*sentNgramRec[i]
                sentPrec[u] += ngramweights[i]*sentNgramPrec[i]
                sentF[u] += ngramweights[i]*sentNgramF[i]
 


            if unitprecrecf:
                sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-F    "+str("%.4f" % sentF[u])+"\n")
                if prec:
                    sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-Prec "+str("%.4f" % sentPrec[u])+"\n")
                if rec:
                    sys.stdout.write(str(nsent)+"::u"+str(u+1)+"-Rec  "+str("%.4f" % sentRec[u])+"\n")


        
        multiSentRec += unitweights[u]*sentRec[u]
        multiSentPrec += unitweights[u]*sentPrec[u]
        multiSentF += unitweights[u]*sentF[u]

        


    # sentence level multiscores

    if sent:
        sys.stdout.write(str(nsent)+"::rgbF    "+str("%.4f" % multiSentF)+"\n")   
        if prec:
            sys.stdout.write(str(nsent)+"::rgbPrec "+str("%.4f" % multiSentPrec)+"\n")
        if rec:
            sys.stdout.write(str(nsent)+"::rgbRec  "+str("%.4f" % multiSentRec)+"\n")
   

    hline = htxt.readline()
    rline = rtxt.readline()

    hypUnits = hline.split("++")
    refUnits = rline.split("++")

        
        
# total precision, recall and F (aritmetic mean of all ngrams and all units)

multiPrec = 0.0
multiRec = 0.0
multiF = 0.0

totRec = [0.0 for y in range(U)] # if separate unit scores are needed
totPrec = [0.0 for y in range(U)]
totF = [0.0 for y in range(U)]


for u in range(U):  
    totalPrec = [0.0 for x in range(n)]
    totalRec = [0.0 for x in range(n)]
    totalF = [0.0 for x in range(n)]

    for i in range(n):
        if totalUnitNgramRefLength[u][i] != 0:
            totalRec[i] = 100 - 100*totalUnitNgramRperCount[u][i]/totalUnitNgramRefLength[u][i]
        else:
            totalRec[i] = 0

        if totalUnitNgramHypLength[u][i] != 0:
            totalPrec[i] = 100 - 100*totalUnitNgramHperCount[u][i]/totalUnitNgramHypLength[u][i]
        else:
            totalPrec[i] = 0

        if totalUnitNgramRefLength[u][i] != 0 or totalUnitNgramHypLength[u][i] != 0:
            totalF[i] = 100 - 100*(totalUnitNgramRperCount[u][i]+totalUnitNgramHperCount[u][i])/(totalUnitNgramRefLength[u][i]+totalUnitNgramHypLength[u][i])
        else:
            totalF[i] = 0

        if ngramprecrecf:
            sys.stdout.write("u"+str(u+1)+"-"+str(i+1)+"gram-F     "+str("%.4f" % totalF[i])+"\n")
            if prec:
                sys.stdout.write("u"+str(u+1)+"-"+str(i+1)+"gram-Prec  "+str("%.4f" % totalPrec[i])+"\n")
            if rec:
                sys.stdout.write("u"+str(u+1)+"-"+str(i+1)+"gram-Rec   "+str("%.4f" % totalRec[i])+"\n")


        totRec[u] += ngramweights[i]*totalRec[i]
        totPrec[u] += ngramweights[i]*totalPrec[i]
        totF[u] += ngramweights[i]*totalF[i]
    

    if unitprecrecf:
        sys.stdout.write("u"+str(u+1)+"-F    "+str("%.4f" % totF[u])+"\n")
        if prec:
            sys.stdout.write("u"+str(u+1)+"-Prec "+str("%.4f" % totPrec[u])+"\n")
        if rec:
            sys.stdout.write("u"+str(u+1)+"-Rec  "+str("%.4f" % totRec[u])+"\n")
 

    multiRec += unitweights[u]*totRec[u]
    multiPrec += unitweights[u]*totPrec[u]
    multiF += unitweights[u]*totF[u]

sys.stdout.write("rgbF    "+str("%.4f" % multiF)+"\n")
if prec:
    sys.stdout.write("rgbPrec "+str("%.4f" % multiPrec)+"\n")
if rec:
    sys.stdout.write("rgbRec  "+str("%.4f" % multiRec)+"\n")



htxt.close()
rtxt.close()











