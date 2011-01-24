#!/usr/bin/env python
import sys
import math
from collections import defaultdict

(nbestFile, paramWeightFile) = sys.argv[1:]

prevIndex = -1
hypCount = 0
diffSums = defaultdict(int)
hypsAtRank = defaultdict(int)

params = [line.strip() for line in open(paramWeightFile)]
paramNames = [line.split('|||')[0].strip().replace(' ','_') for line in params]
paramWeights = [float(line.split('|||')[1].strip().split()[0]) for line in params if 'normalization' not in line]

for line in open(nbestFile):
    (index, translation, feats, overall) = line.strip().split(' ||| ')
    overall = float(overall)
    
    if index != prevIndex:
        n = 0
        prevIndex = index
        hypCount += 1
        vec = [float(feat) for feat in feats.split()]
        try:
            totalVec = [ feat+acc for feat, acc in zip(totalVec, vec)]
        except NameError:
            totalVec = vec
        topBestOverall = overall

    n += 1
    hypsAtRank[n] += 1
    
    if n > 1:
        diff = math.fabs(topBestOverall - overall)
        diffSums[n] += diff

avgVec = [ x / hypCount for x in totalVec ]

for name, feat in zip(paramNames, avgVec):
    print 'TopBestAverage.%s\t%0.2f'%(name, feat)

weightedFeats = []
for name, weight, feat in zip(paramNames, paramWeights, avgVec):
    weightedFeat = feat * weight
    weightedFeats.append(weightedFeat)
    print 'TopBestAverageWeighted.%s\t%0.2f'%(name, weightedFeat)

contributionSum = sum( math.fabs(x) for x in weightedFeats )
contributions = [ math.fabs(x) / contributionSum * 100 for x in weightedFeats ]
for name, contribution in zip(paramNames, contributions):
    print 'TopBestAverageContribution.%s\t%0.2f'%(name, contribution) + '%'

for name, weight in zip(paramNames, paramWeights):
    print 'Weight.%s\t%0.2f'%(name, weight)

i = 2
nBest = hypsAtRank[1]
while hypsAtRank[i] > 0 and i < 100:
    avgDiff = diffSums[i] / hypsAtRank[i]
    print 'AvgOverallDifference1-%d\t%0.2f'%(i,avgDiff)
    i += 1
