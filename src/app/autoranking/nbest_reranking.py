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

def get_nbest_translations(nbestfile):
    pattern = re.compile("(\d*) \|\|\| (.*) \|\|\| ")
    
    previous_sentence_id = 0
    translations = []
    with open(nbestfilename) as nbestfile:
        for line in nbestfile:
            sentence_id, string =  re.findall(pattern, line)
            if sentence_id != previous_sentence_id:
                yield translations
                translations = []
            
            translations.append(SimpleSentence(string))
    yield translations

def get_sources(sourcefilename):
    with open(sourcefilename) as sourcefile:
        for line in sourcefile:
            yield SimpleSentence(line)


class NbestProcessor:
    
    def __init__(self, classifiername, configfilenames):
        self.ranker = Autoranking(configfilenames, classifiername)
    
    def process_files(self, sourcefilename, nbestfilename, outputfilename):
        outputfile = open(outputfilename, 'w')
        for source, translations in izip(get_sources(sourcefilename), get_nbest_translations()):
            ranked_parallelsentence, metadata = self.ranker.get_ranked_sentence(source, translations)
            
            ordered_translations = sorted(ranked_parallelsentence.get_translations(), key=lambda translation: float(translation["rank"])) 
            best_translation = ordered_translations[0]
            
            outputfile.write("{}\n".format(best_translation.get_string()))
                
        
#Please decode with   -include-segmentation-in-n-best
if __name__ == '__main__':
    sourcefilename = sys.argv[1]
    nbestfilename = sys.argv[2]
    classifiername = sys.argv[3]
    outputfilename = sys.argv[4]
    configfilenames = sys.argv[5:]

    nbestprocessor = NbestProcessor(classifiername, configfilenames)
    nbestprocessor.process_files(sourcefilename, nbestfilename, outputfilename)
    
        
    
    