#!/usr/bin/env python
from __future__ import division
import sys
from collections import defaultdict

try:
    from nltk import Tree
except:
    print >>sys.stderr, 'This script requires NLTK from http://www.nltk.org/download'
    sys.exit(1)

parseFile = sys.argv[1]

nSentences = 0
nTokens = 0
nNonterms = 0
heightTotal = 0
minHeight = sys.maxint
maxHeight = 0
nonterms = defaultdict(int)
types = set()

for line in open(parseFile):
    try:
        parse = line.strip()

        if nSentences < 10:
            print 'sample.%d\t%s'%(nSentences+1, parse)

        tree = Tree(line)
        tokens = tree.leaves()
        for token in tokens:
            types.add(token)
        tokenCount = len(tokens)
        height = tree.height()
        for sub in tree.subtrees():
            nonterm = sub.node
            nNonterms += 1
            nonterms[nonterm] += 1

        nTokens += tokenCount
        heightTotal += height
        maxHeight = max(height, maxHeight)
        minHeight = min(height, minHeight)
        
    except:
        pass

    nSentences += 1

avgHeight = heightTotal / nSentences
avgLength = nTokens / nSentences
avgNonterms = nNonterms / nSentences

print 'SentenceCount\t%d'%nSentences
print 'WordTokenCount\t%d'%nTokens
print 'WordTypeCount\t%d'%len(types)
print 'AvgSentenceLength\t%f'%avgLength
print 'NontermTokenCount\t%d'%nNonterms
print 'NontermTypeCount\t%d'%len(nonterms)
print 'AvgNontermTokensPerSentence\t%f'%avgNonterms
print 'AvgHeight\t%f'%avgHeight
print 'MinHeight\t%d'%minHeight
print 'MaxHeight\t%d'%maxHeight

for nonterm, count in nonterms.iteritems():
    try:
        print 'NontermTotal.%s\t%d'%(nonterm, count)
    except:
        print >>sys.stderr, sys.exc_info()[0]

for nonterm, count in nonterms.iteritems():
    try:
        avgCount = count / nSentences
        print 'NontermAvg.%s\t%f'%(nonterm, avgCount)
    except:
        print >>sys.stderr, sys.exc_info()[0]

