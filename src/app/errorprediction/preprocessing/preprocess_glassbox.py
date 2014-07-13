'''
Preprocessing functions for the data on the predicting errors from glassbox MT features 
Highly adapted on TaraXU file structure (particularly eval round 2)

Created on 11 Apr 2013
@author: Eleftherios Avramidis
'''

from featuregenerator.glassbox.moses.extractor import MosesGlassboxExtractor
from dataprocessor.sax.saxps2jcml import IncrementalJcml
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from db import DbConnector
from featuregenerator.hjerson import BinaryHjerson, Hjerson
import re
import os
import sys
import logging


def _get_id_from_line(testset_type, id_line):
    """
    Reconstruct the unique sentence id from a `links` file that is row-by-row aligned to the source file
    This is based on IDing conventions from the 2nd evaluation round of the TaraX\H{U} project
    @param testset_type: it specifies the type of the testset_type, which defines the prefix and possible special IDing behaviour
    @type testset_type: str
    @param id_line: the line with the ID entries
    @type testset_type: str
    """
    
    segment_id, document_id = id_line.split('\t')[1:]
#    if testset_type in ["wmt11", "openoffice3", "wmt10"]:
    uid = "{}-{}-{}".format(testset_type, document_id.strip(), segment_id)
#    else:
#        uid = "{}-{}-{}".format(testset_type, document_id.strip(), segment_id)
    return uid
        
    

def extract_glassbox_features_moses(source_filename, ids_filename, testset_type, moses_target_filename, log_filename, output_filename, source_lang, target_lang, backoff_reference=True, hjersoncounts=False):
    """
    Extract the glassbox features from Moses
    @param source_filename: the filename of a plain text file with one source sentence per line
    @type source_filename: str
    @param target_filename: the filename of a plain text file with one target sentence per line
    @type target_filename: str
    @param log_filename: the filename of the lof of the verbose output produced by Moses decoder
    @type log_filename: 
    """
    
    system = "moses"
    
    #get moses glass features in a list
    extractor = MosesGlassboxExtractor()
    features_dicts = extractor.create_dicts_of_sentences_attributes(log_filename)
    
    #initialize feature generators
    if not hjersoncounts:
        hjerson = BinaryHjerson(lang = target_lang)
    else:
        hjerson = Hjerson(lang = target_lang)
    
    #open readers for input files and a writer for xml
    sourcefile = open(source_filename, 'r')
    moses_targetfile = open(moses_target_filename, 'r')
    idsfile = open(ids_filename, 'r')
    output_xml = IncrementalJcml(output_filename)

    #open a connection to the mySQL server
    mydb = DbConnector()
    
    no_postediting_count = 0
    reference_backoff_count = 0
    
    for source_sentence, id_line, target_sentence, features_dict in zip(sourcefile, idsfile, moses_targetfile, features_dicts):
        uid = _get_id_from_line(testset_type, id_line)
        
        if uid==None:
            sys.exit("Empty unique sentence id {}".format(id_line))
        
        #prepare existing attributes
        tgt_attributes = features_dict 
        atts = {"uid": uid, "langsrc" : source_lang, "langtgt" : target_lang }
        
        #fetch post-edited output, to be used as reference for extracting error classification
        reference = mydb.fetch_postediting(uid, system, source_lang, target_lang)
        if not reference:
            reference = mydb.fetch_reference(uid, target_lang)
            if reference and backoff_reference:
                reference_backoff_count +=1
            else:
                no_postediting_count +=1
                continue
            
        #create ParallelSentence object and write to XML
        parallelsentence = ParallelSentence(SimpleSentence(source_sentence),
                                            [SimpleSentence(target_sentence, tgt_attributes)],
                                            SimpleSentence(reference),
                                            atts)
         
        
        #the rest of the features will be fetched by feature processors on sentence-level
        parallelsentence = hjerson.add_features_parallelsentence(parallelsentence)
        output_xml.add_parallelsentence(parallelsentence)
        
    sourcefile.close()
    moses_targetfile.close()
    idsfile.close()
    output_xml.close()
    logging.warning("{} references were used instead, because no post-editing found".format(reference_backoff_count))
    logging.warning("{} sentences were skipped because no references found".format(no_postediting_count))


def extract_glassbox_features_lucy():
    pass









    

if __name__ == '__main__':
    #print db.retrieve_uid("Deutsch", ['069592001_cust1-069592001-2'])
    source_filename = os.path.expanduser("~/taraxu_data/r2/glassbox/wmt11.de-en.de.dev")
    ids_filename = os.path.expanduser("~/taraxu_data/r2/glassbox/wmt11.de-en.de.links.dev")
    target_filename = os.path.expanduser("~/taraxu_data/r2/glassbox/wmt11.dev")
    log_filename = os.path.expanduser("~/taraxu_data/r2/glassbox/wmt11.v2.log.8.dev")
    testset_type = "wmt11"
    output_filename = os.path.expanduser("~/taraxu_data/r2/glassbox/wmt11.gb.jcml")
    source_lang = "de"
    target_lang = "en"
    
    sth = logging.StreamHandler()
    sth.setLevel(logging.DEBUG)
    
    extract_glassbox_features_moses(source_filename, ids_filename, testset_type, target_filename, log_filename, output_filename, source_lang, target_lang)
    
    
    
