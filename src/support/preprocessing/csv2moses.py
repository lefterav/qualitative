'''
Created on Apr 12, 2016

@author: lefterav
'''
import argparse
from csv import DictReader
import csv
import sys
import xmlrpclib

from mt.moses import MtMonkeyWorker, WsdMosesWorker
from mt.lucy import LucyWorker, AdvancedLucyWorker
from mt.hybrid import LcMWorker

url = "http://blade-3.dfki.uni-sb.de:8100/translate"
proxy = xmlrpclib.ServerProxy(url)


def get_source_sentences(csvfile):
    csvreader = DictReader(csvfile)
    for row in csvreader:
        source = row["Source"]
        id_test_point = row["ID test point"]
        id_version = row["ID version of test point"]
        yield source, id_test_point, id_version

def write_sentences(source_sentences):
    for source in source_sentences:
        if source != "":
            print source
 
def translate_sentences(translator, source_sentences, writer):
    for source, id_test_point, id_version in source_sentences:
        if source != "":
            translation, _ = translator.translate(source)
        else:
            translation = ""
        try:
            writer.writerow([id_test_point, id_version, translation.encode('utf-8')])
        except UnicodeDecodeError: #translation type varies between unicode and string
            writer.writerow([id_test_point, id_version, translation])


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
    input = sys.stdin 
    output = sys.stdout
    
    parser = argparse.ArgumentParser(description="Run translate engine on a file")
    parser.add_argument("--engine")
    parser.add_argument("--url")
    parser.add_argument("--wsd")
    parser.add_argument("--lcmurl")
    parser.add_argument("--output")
    parser.add_argument("--srclang")
    parser.add_argument("--tgtlang")
    parser.add_argument("--subject", default="(DP TECH CTV ECON)")

    args = parser.parse_args()
    
    source_sentences = get_source_sentences(input)
    translator = select_translator(args)
    if args.output:
        with open(args.output, 'w') as outfile:
            writer = csv.writer(outfile, dialect='excel')
            translate_sentences(translator, source_sentences, writer)
    else:
        writer = csv.writer(sys.stdout, dialect='excel')
        translate_sentences(translator, source_sentences, writer)
    
