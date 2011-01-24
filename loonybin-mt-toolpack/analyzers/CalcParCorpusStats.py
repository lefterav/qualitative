#!/usr/bin/env python

from __future__ import division
from collections import defaultdict
import sys
import os.path

if len(sys.argv) == 3:
    (numFolds, srcFilename) = sys.argv[1:]
    tgtFilename, devSrcFilename, devTgtFilename = '', '', ''
elif len(sys.argv) == 4:
    (numFolds, srcFilename, tgtFilename) = sys.argv[1:]
    devSrcFilename, devTgtFilename = '', ''
else:
    (numFolds, srcFilename, tgtFilename, devSrcFilename, devTgtFilename) = sys.argv[1:]

def sopen(filename):
    if filename.endswith('.gz'):
        import gzip
        return gzip.open(filename)
    else:
        return open(filename)

srcFile = sopen(srcFilename)
if tgtFilename:
    tgtFile = sopen(tgtFilename)
nFolds = int(numFolds)

srcLineCount = 0
srcTokenCount = 0
srcMinTokens = 9999
srcMaxTokens = 0
srcTypes = defaultdict(int)
srcLengthDist = defaultdict(int)

tgtLineCount = 0
tgtTokenCount = 0
tgtMinTokens = 9999
tgtMaxTokens = 0
tgtTypes = defaultdict(int)
tgtLengthDist = defaultdict(int)

mostUnbalancedRatio = 1.0
balanceRatioSum = 0.0

class TrainFoldStats:
    def __init__(self):
        self.srcVocab = set()
        self.srcTokenCount = 0
        self.srcSentCount = 0
        self.tgtVocab = set()
        self.tgtTokenCount = 0
        self.tgtSentCount = 0

class TestFoldStats:
    def __init__(self):
        self.srcTypes = defaultdict(int)
        self.srcTokenCount = 0
        self.srcSentCount = 0
        self.tgtTypes = defaultdict(int)
        self.tgtTokenCount = 0
        self.tgtSentCount = 0
        
        # To be filled in at end
        self.srcOovTokens = 0
        self.srcOovTokenRate = 0
        self.srcOovTypes = 0
        self.srcOovTypeRate = 0
        self.tgtOovTokens = 0
        self.tgtOovTokenRate = 0
        self.tgtOovTypes = 0
        self.tgtOovTypeRate = 0

        self.trainTokenCountSrc = 0
        self.trainSentCountSrc = 0
        self.trainTokenCountTgt = 0
        self.trainSentCountTgt = 0

trainForFold = [TrainFoldStats() for i in range(nFolds)]
testForFold = [TestFoldStats() for i in range(nFolds)]

for src in srcFile:
    toks = src.strip().split()

    nFold = srcLineCount % nFolds
    srcLineCount += 1
    nSrcTokens = len(toks)
    srcLengthDist[nSrcTokens] += 1
    srcTokenCount += nSrcTokens
    srcMaxTokens = max(srcMaxTokens, nSrcTokens)
    srcMinTokens = min(srcMinTokens, nSrcTokens)
    for tok in toks:
        srcTypes[tok] += 1
        for i in range(nFolds):
            if i == nFold:
                testForFold[i].srcTypes[tok] += 1
                testForFold[i].srcTokenCount += 1
            else:
                trainForFold[i].srcVocab.add(tok)
                trainForFold[i].srcTokenCount += 1
    for i in range(nFolds):
        if i == nFold:
            testForFold[i].srcSentCount += 1
        else:
            trainForFold[i].srcSentCount += 1

    if tgtFilename:
        tgt = tgtFile.next()
    else:
        tgt = ''
        
    if tgt:
        toks = tgt.strip().split()
        
        tgtLineCount += 1
        nTgtTokens = len(toks)
        tgtTokenCount += nTgtTokens
        tgtLengthDist[nTgtTokens] += 1
        tgtMaxTokens = max(tgtMaxTokens, nTgtTokens)
        tgtMinTokens = min(tgtMinTokens, nTgtTokens)
        for tok in toks:
            tgtTypes[tok] += 1
            for i in range(nFolds):
                if i == nFold:
                    testForFold[i].tgtTypes[tok] += 1
                    testForFold[i].tgtTokenCount += 1
                else:
                    trainForFold[i].tgtVocab.add(tok)
                    trainForFold[i].tgtTokenCount += 1
        for i in range(nFolds):
            if i == nFold:
                testForFold[i].tgtSentCount += 1
            else:
                trainForFold[i].tgtSentCount += 1

        try:
            balanceRatio = nSrcTokens / nTgtTokens
        except ZeroDivisionError:
            balanceRatio = 9999
        mostUnbalancedRatio = max(mostUnbalancedRatio, balanceRatio)
        balanceRatioSum += balanceRatio

if tgtFilename:
    for tgt in tgtFile:
        tgtLineCount += 1

        if srcLineCount != tgtLineCount:
            print >>sys.stderr, "ERROR: Unbalanced source and target corpora:", srcFile, "has", srcLineCount, "lines; ",tgtFile, "has", tgtLineCount, "lines."
            exit(1)

try:
    srcAvgTokens = srcTokenCount / srcLineCount
except ZeroDivisionError:
    srcAvgTokens = 0


srcTypeCount = len(srcTypes)
srcSingletonCount = sum(count==1 for (tok, count) in srcTypes.iteritems())

if tgtFilename:
    tgtTypeCount = len(tgtTypes)
    tgtSingletonCount = sum(count==1 for (tok, count) in tgtTypes.iteritems())

    try:
        tgtAvgTokens = tgtTokenCount / tgtLineCount
    except ZeroDivisionError:
        tgtAvgtTokens = 0

    try:
        avgBalanceRatio = balanceRatioSum / srcLineCount
    except ZeroDivisionError:
        avgBalanceRatio = 0
        
    try:
        lengthRatio = srcTokenCount / tgtTokenCount
    except ZeroDivisionError:
        lengthRatio = 0

# If user provided a dev corpus, calculate OOV statistics
def calcOov(types, devFilename):
    devTokens = 0
    devTypes = set()

    oovTokens = 0
    for line in sopen(devFilename):
        toks = line.strip().split()
        devTokens += len(toks)
        devTypes.update(toks)
        for tok in toks:
            if tok not in types:
                oovTokens += 1

    oovTypes = 0
    for type in devTypes:
        if type not in types:
            oovTypes += 1

    try:
        tokenOovRate = oovTokens / devTokens
    except ZeroDivisionError:
        tokenOovRate = 0

    try:
        typeOovRate = oovTypes / len(devTypes)
    except ZeroDivisionError:
        typeOovRate = 0
    
    return oovTokens, oovTypes, tokenOovRate, typeOovRate

if devSrcFilename:
    (srcOovTokens, srcOovTypes, srcTokenOovRate, srcTypeOovRate) = calcOov(srcTypes, devSrcFilename)
else:
    (srcOovTokens, srcOovTypes, srcTokenOovRate, srcTypeOovRate) = (-1, -1, -1, -1)
    
if devTgtFilename:
    (tgtOovTokens, tgtOovTypes, tgtTokenOovRate, tgtTypeOovRate) = calcOov(tgtTypes, devTgtFilename)
else:
    (tgtOovTokens, tgtOovTypes, tgtTokenOovRate, tgtTypeOovRate) = (-1, -1, -1, -1)

# Calculate OOV rate on training corpus via nFold cross validation
folds = []
for i in range(nFolds):

    srcOovTokenRate = 0
    srcOovTypeRate = 0
    tgtOovTokenRate = 0
    tgtOovTypeRate = 0

    test = testForFold[i]
    train = trainForFold[i]

    for tok, count in test.srcTypes.iteritems():
        if tok not in train.srcVocab:
            test.srcOovTypes += 1
            test.srcOovTokens += count
    try:
        test.srcOovTokenRate = test.srcOovTokens / test.srcTokenCount
    except ZeroDivisionError:
        test.srcOovTokenRate = 0
    try:
        test.srcOovTypeRate = test.srcOovTypes / len(test.srcTypes)
    except ZeroDivisionError:
        test.srcOovTypeRate = 0
    try:
        test.trainTokenCountSrc = train.srcTokenCount
    except ZeroDivisionError:
        test.trainTokenCountSrc = 0
    try:
        test.trainSentCountSrc = train.srcSentCount
    except ZeroDivisionError:
        test.trainSentCountSrc = 0

    if tgtFilename:
        for tok, count in test.tgtTypes.iteritems():
            if tok not in train.tgtVocab:
                test.tgtOovTypes += 1
                test.tgtOovTokens += count
        try:
            test.tgtOovTokenRate = test.tgtOovTokens / test.tgtTokenCount
        except ZeroDivisionError:
            test.tgtoovTokenRate = 0
        try:
            test.tgtOovTypeRate = test.tgtOovTypes / len(test.tgtTypes)
        except ZeroDivisionError:
            test.tgtOovTypeRate = 0
        try:
            test.trainTokenCountTgt = train.tgtTokenCount
        except ZeroDivisionError:
            test.trainTokenCountTgt = 0
        try:
            test.trainSentCountTgt = train.tgtSentCount
        except ZeroDivisionError:
            test.trainSentCountTgt = 0

    folds.append( (test.srcOovTokenRate, test) )

# Now find best, worst, and average statistics for folds
folds = sorted(folds)
(bestRate, bestFold) = folds[0]
(worstRate, worstFold) = folds[-1]
avgFold = TestFoldStats()
for i in range(nFolds):
    avgFold.srcOovTokens += testForFold[i].srcOovTokens / nFolds
    avgFold.srcOovTokenRate += testForFold[i].srcOovTokenRate / nFolds
    avgFold.srcOovTypes += testForFold[i].srcOovTypes / nFolds
    avgFold.srcOovTypeRate += testForFold[i].srcOovTypeRate / nFolds
    avgFold.tgtOovTokens += testForFold[i].tgtOovTokens / nFolds
    avgFold.tgtOovTokenRate += testForFold[i].tgtOovTokenRate / nFolds
    avgFold.tgtOovTypes += testForFold[i].tgtOovTypes / nFolds
    avgFold.tgtOovTypeRate += testForFold[i].tgtOovTypeRate / nFolds

    avgFold.srcTokenCount += testForFold[i].srcTokenCount / nFolds
    avgFold.srcSentCount += testForFold[i].srcSentCount / nFolds
    avgFold.tgtTokenCount += testForFold[i].tgtTokenCount / nFolds
    avgFold.tgtSentCount += testForFold[i].tgtSentCount / nFolds

    avgFold.trainTokenCountSrc += testForFold[i].trainTokenCountSrc / nFolds
    avgFold.trainTokenCountTgt += testForFold[i].trainTokenCountTgt / nFolds
    avgFold.trainSentCountSrc += testForFold[i].trainSentCountSrc / nFolds

# Only differentiate source from target if we are processing a parallel corpus
if tgtFilename:
    label = 'src.'
else:
    label = ''

stats = []
stats.append( ('Folds', numFolds))
if tgtFilename:
    stats.append( ('BalanceRatioMax', mostUnbalancedRatio))
    stats.append( ('BalanceRatioAvg', avgBalanceRatio))
    stats.append( ('LengthRatioSrcOverTgt', lengthRatio))
stats.append( (label+'LineCount', srcLineCount))
stats.append( (label+'TokenCount', srcTokenCount))
stats.append( (label+'TokenCountMin', srcMinTokens))
stats.append( (label+'TokenCountMax', srcMaxTokens))
stats.append( (label+'TokenCountAvg', srcAvgTokens))
stats.append( (label+'TypeCount', srcTypeCount))
stats.append( (label+'LengthDistribution', ' '.join(
    [ str(toks)+'='+str(count) for (toks, count) in sorted(srcLengthDist.iteritems())])) )
for fold, foldName in [(avgFold, 'Avg'), (bestFold, 'Best'), (worstFold, 'Worst')]:
    stats.append( (label+'%sFoldOovTokens' % foldName, fold.srcOovTokens))
    stats.append( (label+'%sFoldOovTokenRate' % foldName, fold.srcOovTokenRate))
    stats.append( (label+'%sFoldOovTypes' % foldName, fold.srcOovTypes))
    stats.append( (label+'%sFoldOovTypeRate' % foldName, fold.srcOovTypeRate))
    stats.append( (label+'%sFoldTrainTokenCount' % foldName, fold.trainTokenCountSrc))
    stats.append( (label+'%sFoldTrainSentCount' % foldName, fold.trainSentCountSrc))
    stats.append( (label+'%sFoldTestSentCount' % foldName, fold.srcSentCount))
    stats.append( (label+'%sFoldTestTokenCount' % foldName, fold.srcTokenCount))
if devSrcFilename:
    stats.append( (label+'DevOovTokens', srcOovTokens))
    stats.append( (label+'DevOovTokenRate', srcTokenOovRate))
    stats.append( (label+'DevOovTypes', srcOovTypes))
    stats.append( (label+'DevOovTypeRate', srcTypeOovRate))
if tgtFilename:
    stats.append( ('tgt.LineCount', tgtLineCount))
    stats.append( ('tgt.TokenCount', tgtTokenCount))
    stats.append( ('tgt.TokenCountMin', tgtMinTokens))
    stats.append( ('tgt.TokenCountMax', tgtMaxTokens))
    stats.append( ('tgt.TokenCountAvg', tgtAvgTokens))
    stats.append( ('tgt.TypeCount', tgtTypeCount))
    stats.append( ('tgt.LengthDistribution', ' '.join(
        [ str(toks)+'='+str(count) for (toks, count) in sorted(tgtLengthDist.iteritems())])) )
    for fold, foldName in [(avgFold, 'Avg'), (bestFold, 'Best'), (worstFold, 'Worst')]:
        stats.append( ('tgt.%sFoldOovTokens' % foldName, fold.tgtOovTokens))
        stats.append( ('tgt.%sFoldOovTokenRate' % foldName, fold.tgtOovTokenRate))
        stats.append( ('tgt.%sFoldOovTypes' % foldName, fold.tgtOovTypes))
        stats.append( ('tgt.%sFoldOovTypeRate' % foldName, fold.tgtOovTypeRate))
        stats.append( ('tgt.%sFoldTrainSentCount' % foldName, fold.trainSentCountTgt))
        stats.append( ('tgt.%sFoldTrainTokenCount' % foldName, fold.trainTokenCountTgt))
        stats.append( ('tgt.%sFoldTestSentCount' % foldName, fold.tgtSentCount))
        stats.append( ('tgt.%sFoldTestTokenCount' % foldName, fold.tgtTokenCount))
if devTgtFilename:
    stats.append( ('tgt.DevOovTokens', tgtOovTokens))
    stats.append( ('tgt.DevOovTokenRate', tgtTokenOovRate))
    stats.append( ('tgt.DevOovTypes', tgtOovTypes))
    stats.append( ('tgt.DevOovTypeRate', tgtTypeOovRate))

for key, value in stats:
    print '%s %s'%(key, value)
