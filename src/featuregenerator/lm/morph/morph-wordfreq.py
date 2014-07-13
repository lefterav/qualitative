'''
Created on 19 Dec 2011

@author: Eleftherios Avramidis
'''
import nltk
import sys
from operator import itemgetter
import codecs

fd = nltk.FreqDist()

filename = sys.argv[1]
filename_out = sys.argv[2]
try:
    encoding_in = sys.argv[3]
except:
    encoding_in = "utf-8"
try:
    encoding_out = sys.argv[4]
except:
    encoding_out = "utf-8"
try:
    limit = int(sys.argv[5])
except:
    limit  = -1

for line in codecs.open(filename, 'r', encoding_in):
    for word in line.split():
            word = word.replace("*", "<STAR>")
            word = word.replace("/", "<SLASH>")
	    word = word.replace("#", "<HASH>")
	    word = word.replace(" ", "_")
	    word = word.replace("+", "<PLUS>")
            word = unicode(word)
            fd.inc(word)
    if limit > -1:  
        if fd.N() > limit:
            break
        

outfile = codecs.open(filename_out, 'w', encoding_out)
for (word, freq) in sorted(fd.items(), key=itemgetter(0)):
    outfile.write( "%s %s\n" % (freq, word) )
