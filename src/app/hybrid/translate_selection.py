'''
Process a text file with 3 translation engines and the selection mechanism

Created on Aug 19, 2016

@author: lefterav
'''

from mt.moses import ProcessedWorker
from mt.neuralmonkey import NeuralMonkeyWorker
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

def parse_args():

    parser = argparse.ArgumentParser(description="Run translate engines and selection mechanism on a file")
    parser.add_argument('--engines', nargs='*', default=['Lucy', 'Moses', 'NeuralMonkey'],
                        help="A list of the names of the engines for translating, in the prefered order")
    parser.add_argument('--translated_textfiles', '-t', nargs='*', default=None,
                        help="If translations have been performed, they can be given here in simple text files \
                        so that only selection takes place. The text filenames should be provided \
                        in respective order to the list of engine names passed by --engines. If this argument is \
                        not given, the translations will be fetched from the given engines")
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
    parser.add_argument('--debug', action='store_true', default=False, help="Run in full verbose mode")   
    parser.add_argument('--reverse', action='store_true', default=False,
                        help="Whether ranker's decisions should be reversed. Useful if ranker trained with BLEU or meteor \
                        and not reversed before it was stored.")
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
    translator = Pilot3Translator(args.engines, args.config, 
                                  args.source_language, 
                                  args.target_language, 
                                  args.ranking_model,
                                  args.reverse)
    
    text_input = codecs.open(args.input, 'r', 'utf8')
    text_output = open(args.text_output, 'w')

    if args.description_output:
        description_output = open(args.description_output, 'w')

    if args.parallelsentence_output:
        parallelsentence_output = IncrementalJcml(args.parallelsentence_output)
        #parallelsentence_output = open(args.parallelsentence_output, 'w')

    counter = 0
    for source in text_input:
        counter+=1
        log.info("Translating sentence {}".format(counter))
        best_translation_string, parallelsentences, description = translator.translate(source)
        text_output.write(best_translation_string)
        text_output.write(os.linesep)
        if args.parallelsentence_output:
            parallelsentence_output.add_parallelsentences(parallelsentences)

        if args.description_output:
            description_output.write(str(description))
            description_output.write(os.linesep)

    text_output.close()
    if args.parallelsentence_output:
        parallelsentence_output.close()
    if args.description_output:
        description_output.close()
        
        
def select_from_translated_textfiles(args):
    selector = Autoranking(args.config, args.ranking_model, 
                           args.source_language, args.target_language, 
                           args.reverse)
    
    sourcefile = args.input
    textfiles = [open(t) for t in args.translated_textfiles]
    
    text_output = open(args.text_output, 'w')

    #if args.description_output:
    #    description_output = open(args.description_output, 'w')

    if args.parallelsentence_output:
        parallelsentence_output = IncrementalJcml(args.parallelsentence_output)
    
    request_id = 0
    for source_string in open(sourcefile):
        request_id += 1
        log.info("Translating sentence {}".format(request_id))
        translation_strings = ([t.readline() for t in textfiles])
        log.debug("Read {} translations".format(len(translation_strings)))
        system_names = args.engines
        selected_translation_string, ranked_sentences = selector.get_best_sentence_from_strings(source_string, 
                                                                                                translation_strings, 
                                                                                                system_names, 
                                                                                                reconstruct='soft',
                                                                                                request_id=request_id)
        log.debug("Writing selected translation for sentence {}".format(request_id))
        print >>text_output, selected_translation_string
        
        if args.parallelsentence_output:
            parallelsentence_output.add_parallelsentences(ranked_sentences)

        #if args.description_output:
        #    description_output.write(str(description))
        #    description_output.write(os.linesep)
    
    text_output.close()
    if args.parallelsentence_output:
        parallelsentence_output.close()
    for t in textfiles:
        t.close()
    
    
    

    
if __name__ == '__main__':
    args = parse_args()
    set_loglevel(args.debug)
    if args.translated_textfiles:
        select_from_translated_textfiles(args)
    else:
        translate_and_select_sourcefile(args)
    

   
    
