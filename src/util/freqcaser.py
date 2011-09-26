# -*- coding: utf-8 -*-
'''
Created on Sep 16, 2011

@author: David Vilar
'''
import gzip
import sys
from nltk.tokenize.punkt import PunktWordTokenizer

class FreqCaser():


    def __init__(self, case_file = None):
        self.caseDict = self.getCaseFreqs(self.openFile(case_file))
        self.dontChangeBeginningOfSentence = [unicode(s, "utf-8") for s in ["-", "(", "¡", "¿", '"']]

    def isZipFile(self, fname):
        fp = open(fname, "rb")
        magic = fp.read(2)
        fp.close()
        return magic == '\x1f\x8b'
    
    def openFile(self, file, allowNone=True):
        """ Returns (fp, name, isZipFile) """
        if not file:
            if allowNone:
                return None
            else:
                raise IOError
        if isinstance(file, str):
            if self.isZipFile(file):
                return gzip.GzipFile(file)
            else:
                return open(file)
        elif isinstance(file, file):
            return file
    
    def getCaseFreqs(self, fp):
        allDict = {}
        for l in fp:
            line = unicode(l, "utf-8")
            words = line.split()
            beginningOfSentence = True
            for w in words:
                if not beginningOfSentence:
                    thisWordDict = allDict.setdefault(w.lower(), {})
                    thisWordDict[w] = 1 + thisWordDict.get(w, 0)
                if w not in self.dontChangeBeginningOfSentence:
                    beginningOfSentence = (w == ".") or (w == "?") or (w == "!") 
    
        caseDict = {}
        for d in allDict.iteritems():
            keysWithFreq = d[1].items()
            keysWithFreq.sort(key = lambda x: x[1], reverse=True)
            caseDict[d[0]] = keysWithFreq[0][0]
    
        return caseDict
    



    def freqcase(self, string):
        words = PunktWordTokenizer().tokenize(string)
        beginningOfSentence = True
        cased_words = []
        for w in words:

            lowerW = w.lower()
            if self.caseDict.has_key(lowerW):
                cased_words.append ( "%s " % self.caseDict[lowerW].encode("utf-8"))
            else:
                cased_words.append("%s " % w.lower().encode("utf-8"))
            if w not in self.dontChangeBeginningOfSentence:
                beginningOfSentence = (w == ".") or (w == "?") or (w == "!") or (w == "#") # \# for mrefs
        return ' '.join(cased_words)
        
        
