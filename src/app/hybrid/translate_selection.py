'''
Process a text file with 3 translation engines and the selection mechanism

Created on Aug 19, 2016

@author: lefterav
'''

from mt.moses import ProcessedWorker
from mt.neuralmonkey import NeuralMonkeyWorker
from mt.hybrid import Pilot3Translator
import argparse
import logging as log
import sys
from dataprocessor.sax.saxps2jcml import IncrementalJcml

def parse_args():

    parser = argparse.ArgumentParser(description="Run translate engines and selection mechanism on a file")
    parser.add_argument('--engines', nargs='*', action='append', default=['Lucy','Moses','NeuralMonkey'],
                        help="A list of the engines to be used for translating, in the prefered order")
    parser.add_argument('--source_language', default='en', help="The language code of the source language")
    parser.add_argument('--target_language', default='de', help="The language code of the target language")
    parser.add_argument('--config', nargs='*', 
                        help="A list of configuration files for the engines and the feature generators")
    parser.add_argument('--ranking_model',
                        help="The path of the file containing a ranker, as a result of the training process")
    parser.add_argument('--input', help="The location of a text file to be translated")
    parser.add_argument('--text_output', help="The location of the text file where translations will be written")
    parser.add_argument('--description_output', default=None,
                        help="The location of the text file where the description of the selection process will be written")
    parser.add_argument('--parallelsentence_output', default=None,
                        help="The location of the JCML file where the full annotated and ranked parallel sentences will be written")
    parser.add_argument('--debug', type=bool, default=False, help="Run in full verbose mode")

    args = parser.parse_args()
    log.debug("Read config filenames from commandline {}".format(args.config))
    return args

def set_loglevel(args):
    loglevel = log.INFO
    if args.debug:
        loglevel = log.DEBUG
    log.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')  

def translate_file(args):
    translator = Pilot3Translator(args.engines, args.config, 
                                  args.source_language, 
                                  args.target_language, 
                                  args.ranking_model)
    
    text_input = open(args.input)
    text_output = open(args.text_output, 'w')

    if args.description_output:
        description_output = open(args.description_output, 'w')

    if args.parallelsentence_output:
        parallelsentence_output = IncrementalJcml(args.parallelsentence_output)

    counter = 0
    for source in text_input:
        counter+=1
        log.info("Translating sentence {}".format(counter))
        best_translation_string, parallelsentences, description = translator.translate_with_selection(source)
        text_output.write(best_translation_string)
        if args.parallelsentence_output:
            parallelsentence_output.add_parallelsentences(parallelsentences)
        if args.description_output:
            description_output.write(str(description))

    text_output.close()
    if args.parallelsentence_output:
        parallelsentence_output.close()
    if args.description_output:
        description_output.close()
    
if __name__ == '__main__':
    args = parse_args()
    set_loglevel(args)
    translate_file(args)

   
    
