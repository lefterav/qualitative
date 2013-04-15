'''
Preprocessing functions for the data on the predicting errors from glassbox MT features 

Created on 11 Apr 2013
@author: Eleftherios Avramidis
'''

from featuregenerator.glassbox.mosesglassbox import MosesGlassboxExtractor
from io_utils.sax.saxps2jcml import IncrementalJcml
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
import re

import os



def _get_id_from_line(id_type, id_line):
    """
    Reconstruct the unique sentence id from a `links` file that is row-by-row aligned to the source file
    This is based on IDing conventions from the 2nd evaluation round of the TaraX\H{U} project
    @param id_type: it specifies the type of the testset, which defines the prefix and possible special IDing behaviour
    @type id_type: str
    @param id_line: the line with the ID entries
    @type id_type: str
    """
    
    if id_type == "wmt11":
        testset = "wmt11"
        segment_id, document_id = id_line.split('\t')[1:]
        uid = "{}-{}-{}".format(testset, segment_id, document_id)
        return uid
    

def extract_glassbox_features_moses(source_filename, ids_filename, id_type, target_filename, log_filename, output_filename):
    """
    Extract the glassbox features from Moses
    @param source_filename: the filename of a plain text file with one source sentence per line
    @type source_filename: str
    @param target_filename: the filename of a plain text file with one target sentence per line
    @type target_filename: str
    @param log_filename: the filename of the lof of the verbose output produced by Moses decoder
    @type log_filename: 
    """
    
    extractor = MosesGlassboxExtractor()
    features_dicts = extractor.create_dicts_of_sentences_attributes(log_filename)
    
    sourcefile = open(source_filename, 'r')
    targetfile = open(target_filename, 'r')
    idsfile = open(ids_filename, 'r')
    
    output_xml = IncrementalJcml(output_filename)

    #remember previous IDs, so that you always get the next one
    previous_ids = []
    
    for source_sentence, id_line, target_sentence, features_dict in zip(sourcefile, idsfile, targetfile, features_dicts):
        uid = _get_id_from_line(id_type, id_line)
        
        if not uid: #if sentence has not been annotated just skip
            continue
        
        previous_ids.append(uid)
        
        #add unique id to the list of the attributes
        attributes = features_dict
        attributes["uid"] = uid
        
#        auto_error_class_attributes = retrieve_auto_error_classification(uid)
#        auto_error_class_attributes = db.retrieve_auto_error_classification(uid)
#        if not auto_error_class_attributes:
#            continue
#        #attributes.update(auto_error_class_attributes)
#        
#        attributes.update(auto_error_class_attributes)
        
        #create ParallelSentence object and write to XML
        parallelsentence = ParallelSentence(SimpleSentence(source_sentence),
                                            [SimpleSentence(target_sentence)],
                                            None,
                                            attributes)
        
        output_xml.add_parallelsentence(parallelsentence)
        
    sourcefile.close()
    targetfile.close()
    idsfile.close()
    output_xml.close()
    


def extract_glassbox_features_lucy():
    pass









    

if __name__ == '__main__':
    #print db.retrieve_uid("Deutsch", ['069592001_cust1-069592001-2'])
    source_filename = "/home/dupo/taraxu_data/r2/glassbox/wmt11.de-en.de.dev"
    ids_filename = "/home/dupo/taraxu_data/r2/glassbox/wmt11.de-en.de.links.dev"
    target_filename = "/home/dupo/taraxu_data/r2/glassbox/wmt11.dev"
    log_filename = "/home/dupo/taraxu_data/r2/glassbox/wmt11.v2.log.8.dev"
    id_type = "wmt11"
    output_filename = "/home/dupo/taraxu_data/r2/glassbox/wmt11.gb.jcml"
    extract_glassbox_features_moses(source_filename, ids_filename, id_type, target_filename, log_filename, output_filename)
    
    
    