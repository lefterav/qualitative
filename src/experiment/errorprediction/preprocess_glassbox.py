'''
Preprocessing functions for the data on the predicting errors from glassbox MT features 

Created on 11 Apr 2013
@author: Eleftherios Avramidis
'''

from featuregenerator.glassbox.mosesglassbox import MosesGlassboxExtractor
from io_utils.sax.saxps2jcml import IncrementalJcml
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from db import retrieve_uid

import os




def extract_glassbox_features_moses(source_filename, target_filename, log_filename, output_filename):
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
    
    output_xml = IncrementalJcml(output_filename)

    #remember previous IDs, so that you always get the next one
    previous_ids = []
    
    for source_sentence, target_sentence, features_dict in (sourcefile, targetfile, features_dicts):
        uid = retrieve_uid(source_sentence, previous_ids)
        
        if not uid: #if sentence has not been annotated just skip
            continue
        
        previous_ids.append(uid)
        
        #add unique id to the list of the attributes
        attributes = features_dict
        attributes["uid"] = uid
        
#        auto_error_class_attributes = retrieve_auto_error_classification(uid)
        manual_error_class_attributes = 
        #attributes.update(auto_error_class_attributes)
        
        
        #create ParallelSentence object and write to XML
        parallelsentence = ParallelSentence(SimpleSentence(source_sentence),
                                            SimpleSentence(target_sentence),
                                            None,
                                            attributes)
        
        output_xml.add_parallelsentence(parallelsentence)
        
    sourcefile.close()
    targetfile.close()
    output_xml.close()
    


def extract_glassbox_features_lucy():
    pass









    

if __name__ == '__main__':
    #print retrieve_uid("Deutsch", ['069592001_cust1-069592001-2'])
    
    