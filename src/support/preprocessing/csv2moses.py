'''
Created on Apr 12, 2016

@author: lefterav
'''
from csv import DictReader
import csv
import sys
import xmlrpclib
import datetime
import sys
from app.hybrid.translate import MtMonkeyWorker, LucyWorker, WsdMosesWorker, LcMWorker
import argparse

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
        writer.writerow([id_test_point, id_version, translation])

def select_translator(args):
    translator_name = "{}Worker".format(args.engine)
    translator_class = eval(translator_name)
    if args.wsd:
        translator = translator_class(args.url, args.wsd)
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

    args = parser.parse_args()
    
    source_sentences = get_source_sentences(input)
    translator = select_translator(args)
    writer = csv.writer(sys.stdout, dialect='excel')
    translate_sentences(translator, source_sentences, writer)
    