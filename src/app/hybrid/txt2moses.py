'''
Created on Apr 12, 2016

@author: lefterav
'''
import argparse
from csv import DictReader
import csv
import sys
import xmlrpclib
import logging as log

from mt.moses import MtMonkeyWorker, WsdMosesWorker
from mt.lucy import LucyWorker, AdvancedLucyWorker
from mt.hybrid import LcMWorker

url = "http://blade-3.dfki.uni-sb.de:8100/translate"
proxy = xmlrpclib.ServerProxy(url)


def select_translator(args):
    translator_name = "{}Worker".format(args.engine)
    translator_class = eval(translator_name)
    if args.wsd:
        translator = translator_class(args.url, args.wsd)
    elif args.engine=="Lucy" or args.engine=="AdvancedLucy":
        translator = translator_class(args.url, source_language=args.srclang,
                                      target_language=args.tgtlang,
                                      subject_areas=args.subject)
    elif args.engine=="LcM":
        translator = translator_class(args.url, args.lcmurl, source_language=args.srclang,
                                      target_language=args.tgtlang,
                                      )
    else:
        translator = translator_class(args.url)
    return translator

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Run translate engine on a file")
    parser.add_argument("--engine")
    parser.add_argument("--url")
    parser.add_argument("--wsd")
    parser.add_argument("--lcmurl")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--srclang")
    parser.add_argument("--tgtlang")
    parser.add_argument("--subject", default="(DP TECH CTV ECON)")

    args = parser.parse_args()
    
    translator = select_translator(args)
    infile = open(args.input)
    i = 0
    with open(args.output, 'w') as outfile:
        for line in infile:
            i += 1
            print i,
            translation, _ = translator.translate(line)
            print >> outfile, translation
    infile.close()
