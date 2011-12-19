'''
Created on 19 Dec 2011

@author: elav01
'''
import nltk
import sys
from operator import itemgetter

fd = nltk.FreqDist()

filename = sys.argv[0]
for line in open(filename, 'r'):
    for word in nltk.word_tokenize(line):
            fd.inc(word)


for word in sorted(fd.items(), key=itemgetter(0)):
    print word