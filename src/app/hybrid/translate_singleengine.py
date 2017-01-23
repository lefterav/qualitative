'''
Created on Sep 26, 2016

@author: Eleftherios Avramidis
'''

from mt.moses import MosesWorker, ProcessedMosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker
from mt.lucy import LucyWorker, AdvancedLucyWorker
import argparse
import logging
import logging as log
import sys
import os
import codecs
from dataprocessor.sax.saxps2jcml import IncrementalJcml
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from ConfigParser import SafeConfigParser
import time

def parse_args():

    parser = argparse.ArgumentParser(description="Run translate a single translation engine on a file")
    parser.add_argument('--engine', default='ProcessedMoses',
                        help= "the name of the engine for translating")
    parser.add_argument('--source_language', default='en', help="The language code of the source language")
    parser.add_argument('--target_language', default='de', help="The language code of the target language")
    parser.add_argument('--config', nargs='*', 
                        help="A list of configuration files for the engines and the feature generators")
    parser.add_argument('--input', help="The location of a text file to be translated")
    parser.add_argument('--text_output', help="The location of the text file where translations will be written")
    parser.add_argument('--subject_areas', help="")
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

def load_worker(config, args):
    worker_kwargs = {'source_language': args.source_language, 
                     'target_language': args.target_language}

    if args.engine=="ProcessedMoses":
        engine_name = "Moses"
        truecaser_section = "Truecaser:{}".format(args.source_language)
        worker_kwargs['truecaser_model'] = config.get(truecaser_section, 'model')
    elif args.engine=="AdvancedLucy":
        engine_name = "Lucy"
        moses_section = "Moses:{}-{}".format(args.source_language, args.target_language)
        worker_kwargs['moses'] = config.get(moses_section, 'uri')
    else:
        engine_name = args.engine

    if engine_name.endswith("Lucy"):
        worker_kwargs.update(config.items(engine_name))
        worker_kwargs['subject_areas'] = args.subject_areas
    else:
        worker_section = "{}:{}-{}".format(engine_name, args.source_language, args.target_language)
        log.info("Loading {}".format(worker_section))
        worker_kwargs.update(config.items(worker_section))
    
    worker_class = eval("{}Worker".format(args.engine))
    worker = worker_class(**worker_kwargs)
    return worker

def translate_file(worker, source_file, target_file):
    source = open(source_file)
    target = open(target_file, 'w')
    
    start_time = time.time()
    i = 0
    for line in source:
        i+=1
        translation, _ = worker.translate(line)
        print >>target, translation
        diff = time.time() - start_time
        log.info("Execution: {} sec, {} sentences".format(round(diff, 0), i))
        log.info("{} sec/sentence" .format(round(1.0 * diff / i, 2)))
        
    target.close()
    source.close()
    log.info("Done")

if __name__ == '__main__':
    args = parse_args()
    set_loglevel(args.debug)
    config = SafeConfigParser()
    config.read(args.config)

    worker = load_worker(config, args)
    translate_file(worker, args.input, args.text_output)

   
