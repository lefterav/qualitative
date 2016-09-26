'''
Created on Sep 26, 2016

@author: Eleftherios Avramidis
'''

from mt.moses import MosesWorker, ProcessedMosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker
from mt.lucy import LucyWorker, AdvancedLucyWorker
from mt.hybrid import Pilot3Translator
import argparse
import logging
import logging as log
import sys
import os
import codecs
from dataprocessor.sax.saxps2jcml import IncrementalJcml
from mt.selection import Autoranking
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from app.hybrid.servers.xmlrpcserver_worker import worker_class
from ConfigParser import SafeConfigParser

def parse_args():

    parser = argparse.ArgumentParser(description="Run translate engines and selection mechanism on a file")
    parser.add_argument('--engine', default='ProcessedMoses',
                        help= "the name of the engine for translating")
    parser.add_argument('--source_language', default='en', help="The language code of the source language")
    parser.add_argument('--target_language', default='de', help="The language code of the target language")
    parser.add_argument('--config', nargs='*', 
                        help="A list of configuration files for the engines and the feature generators")
    parser.add_argument('--input', help="The location of a text file to be translated")
    parser.add_argument('--text_output', help="The location of the text file where translations will be written")
    parser.add_argument('--debug', action='store_true', default=False, help="Run in full verbose mode")   
    args = parser.parse_args()
    return args

def set_loglevel(debug=False):
    loglevel = log.INFO
    if debug:
        print "Enable debug verbose mode"
        loglevel = log.DEBUG
        log.basicConfig(level=loglevel,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    log.debug("Setting verbose output ON")


def translate_and_select_sourcefile(args):
    log.info("Engines: {}".format(args.engines)) 

if __name__ == '__main__':
    args = parse_args()
    config = SafeConfigParser()
    config.read(args.config)
    worker_kwargs = config.items(args.engine)

    worker_class = eval("{}Worker".format(args.engine))
    worker = worker_class(worker_kwargs)
    