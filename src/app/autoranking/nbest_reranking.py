'''
Perform reranking of n-best lists
Created on 4 Aug 2014

@author: Eleftherios Avramidis
'''

import argparse
import sys
from application import Autoranking
from sentence.sentence import SimpleSentence
import re
from itertools import izip
from multiprocessing import Pool

import logging

def get_nbest_translations(nbestfilename, n=10):
    pattern = re.compile("(\d*) \|\|\| (.*) \|\|\| .* ")
    
    previous_sentence_id = '0'
    translations = []

    nbestfile = open(nbestfilename)
    for line in nbestfile:
        sentence_id, string = re.findall(pattern, line)[0]
        sys.stderr.write("sentence id {}\n".format(sentence_id))
        if sentence_id != previous_sentence_id:
            yield translations
            previous_sentence_id = sentence_id
            translations = []
        if len(translations) < n:
            attributes = {'system': 'n_{}'.format(sentence_id)}
            translations.append(SimpleSentence(string, attributes))
    nbestfile.close()
    if translations:
        yield translations

def get_sources(sourcefilename):
    sourcefile = open(sourcefilename)
    for line in sourcefile:
        yield SimpleSentence(line)
    sourcefile.close()


class NbestProcessor:
    
    def __init__(self, classifiername, configfilenames):
        self.ranker = Autoranking(configfilenames, classifiername)
    
    def process_files(self, sourcefilename, nbestfilename, outputfilename):
        outputfile = open(outputfilename, 'w')
        for source, translations in izip(get_sources(sourcefilename), get_nbest_translations(nbestfilename)):
            if len(translations)==1:
                outputfile.write("{}\n".format(translations[0]))
                continue

            sys.stderr.write("translations: {}".format(translations))
            ranked_parallelsentence, metadata = self.ranker.get_ranked_sentence(source, translations)
            
            ordered_translations = sorted(ranked_parallelsentence.get_translations(), key=lambda translation: float(translation["rank"])) 
            best_translation = ordered_translations[0]
            
            outputfile.write("{}\n".format(best_translation.get_string()))
        outputfile.close()
                
        
#Please decode with   -include-segmentation-in-n-best
if __name__ == '__main__':
    sourcefilename = sys.argv[1]
    nbestfilename = sys.argv[2]
    classifiername = sys.argv[3]
    outputfilename = sys.argv[4]
    configfilenames = sys.argv[5:]

   # FORMAT = "%(asctime)-15s %(clientip)s %(user)-8s %(message)s"
   # logging.basicConfig(format=FORMAT, level=logging.DEBUG)  
    
   # logging.debug("Logging enabled")
    nbestprocessor = NbestProcessor(classifiername, configfilenames)
    nbestprocessor.process_files(sourcefilename, nbestfilename, outputfilename)
    
    
    
