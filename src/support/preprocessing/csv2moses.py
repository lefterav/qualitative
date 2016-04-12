'''
Created on Apr 12, 2016

@author: lefterav
'''
from csv import DictReader
import sys
import xmlrpclib
import datetime
import sys
from app.hybrid.translate import MosesWorker, LucyWorker, MtMonkeyWorker, WSDclient

url = "http://blade-3.dfki.uni-sb.de:8100/translate"
proxy = xmlrpclib.ServerProxy(url)



def get_source_sentences(csvfile):
    csvreader = DictReader(csvfile)
    for row in csvreader:
        source = row["Source"]
        #id_test_point = row["ID test point"]
        #id_version = row["ID version of test point"]
        yield source

def write_sentences(source_sentences):
    for source in source_sentences:
        if source != "":
            print source
 
def translate_sentences(source_sentences):
    for source in source_sentences:
        if source != "":
            print source
            
            request = {"action": "translate",
                    "sourceLang": "de",
                    "targetLang": "en",
                    "text": source}
            result = proxy.server.process_task(request)
            print result
           


if __name__ == '__main__':
    input = sys.stdin 
    output = sys.stdout
    source_sentences = get_source_sentences(input)
    translate_sentences(source_sentences)
    
    
    