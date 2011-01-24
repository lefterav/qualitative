#!/usr/bin/env python
import sys

arpaFile = sys.argv[1]

#\data\
#ngram 1=2934293
#ngram 2=36275631
#ngram 3=44345904
#ngram 4=63029411

f = open(arpaFile)
for line in f:
    if line.strip() == '\\data\\':
        break

for line in f:
    line = line.strip()
    if line.startswith('ngram'):
        (ngram, counts) = line.split()
        (n, count) = counts.split('=')
        print '%s-grams\t%s' % (n,count)
    elif line.startswith('\\'):
        break

