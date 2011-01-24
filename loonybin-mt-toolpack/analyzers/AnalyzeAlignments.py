#!/usr/bin/env python
from __future__ import division
import sys

(alignmentFilename, srcFilename, tgtFilename) = sys.argv[1:]

def shell(cmd):
    import sys,subprocess
    code = subprocess.Popen(cmd, shell=True).wait()
    if code != 0:
        sys.exit(1)

def sopen(filename):
    if filename.endswith('.gz'):
        import gzip
        return gzip.open(filename)
    else:
        return open(filename)

alignmentFile = sopen(alignmentFilename)
srcFile = sopen(srcFilename)
tgtFile = sopen(tgtFilename)

linkCount = 0
srcWordCount = 0
tgtWordCount = 0
sentenceCount = 0

maxLinksPerSrcWord = 0
maxLinksPerTgtWord = 0

def tupleIter(a, b, c):
    for aLine in a:
        bLine, cLine = b.next(), c.next()

        # TODO: Check length of B,C -- AND A
        yield aLine, bLine, cLine
    # TODO: Make sure we don't have any leftover lines

for alignment, src, tgt in tupleIter(alignmentFile, srcFile, tgtFile):
    
    links = alignment.strip().split()
    nLinks = len(links)
    linkCount += nLinks

    srcToks = src.strip().split()
    tgtToks = tgt.strip().split()
    nSrcToks = len(srcToks)
    nTgtToks = len(tgtToks)
    srcWordCount += nSrcToks
    tgtWordCount += nTgtToks

    maxLinksPerSrcWord = max(maxLinksPerSrcWord, nLinks / nSrcToks )
    maxLinksPerTgtWord = max(maxLinksPerTgtWord, nLinks / nTgtToks )
    
    sentenceCount += 1

linksPerSent = linkCount / sentenceCount
avgLinksPerSrcWord = linkCount / srcWordCount
avgLinksPerTgtWord = linkCount / tgtWordCount

stats = []
stats.append(('LinksPerSent', linksPerSent))
stats.append(('AvgLinksPerSrcWord', avgLinksPerSrcWord))
stats.append(('AvgLinksPerTgtWord', avgLinksPerTgtWord))
stats.append(('MaxLinksPerSrcWord', maxLinksPerSrcWord))
# TODO: Number of unaligned words
stats.append(('SrcWordCount', srcWordCount))
stats.append(('TgtWordCount', tgtWordCount))
stats.append(('SentenceCount', sentenceCount))

for key, value in stats:
    print '%s\t%s'%(key, value)
