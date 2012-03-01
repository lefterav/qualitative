'''
Created on 29 Feb 2012

@author: elav01
'''


import re
import sys
import os
import subprocess
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

from io.sax.saxps2jcml import Parallelsentence2Jcml
from io.input.jcmlreader import JcmlReader



class ImportDecodingFeatures:
    
    def __init__(self, path="/home/elav01/taraxu_data/wmt12/quality-estimation/training_set/decoding"):
        self.path = path

    
    

        
        

class LanguageCheckerCmd(LanguageFeatureGenerator):
    
    def __init__(self, lang="", commandline=[]):
        self.lang = lang
    
    def add_features_batch(self, parallelsentences):
        process = subprocess.Popen(['commandline', 'test2.py'], shell=False, stdin=subprocess.PIPE)
#        process.communicate(parallelsentence.get_)
    
    
    def offline_process(self, filename_input, filename_output, existing_jcml):
        dataset = JcmlReader(existing_jcml).get_dataset()
        size = dataset.get_size()
        file_input = open(filename_input, 'r')
        file_content = file_input.read()
        att_vector = self._get_att_vector(file_content, size)
        dataset.add_attribute_vector(att_vector)
        
        Parallelsentence2Jcml(dataset.get_parallelsentences()).write_to_file(filename_output)

    
    def _get_att_vector(self, file_content, size):
        
        
        pattern = "\d*.\) Line (\d*), column \d*, Rule ID: (.*)\n"
        
        feature_entries = re.findall(pattern, file_content)
        feature_entries = [(int(key), value.replace("[", "_").replace("]", "_")) for  (key, value) in feature_entries]
        errors_per_sentence = {}
        possible_error_ids = set()
        #first make one list of error ids per sentence 
        for sentence_id , error_id in feature_entries:
            possible_error_ids.add(error_id)
            try:
                errors_per_sentence[sentence_id-1].append(error_id)
            except KeyError:
                errors_per_sentence[sentence_id-1] = [error_id]
                
        #construct a vector of dictionaries with counts
        vector_atts = []
        for i in range(0, size+1):
            atts = {}
            for error_id in possible_error_ids:
                error_label = "lgt_{0}".format(error_id).lower()
                atts[error_label] = 0  
            try:
                for error_id in errors_per_sentence[i]:
                    error_label = "lgt_{0}".format(error_id).lower()
                    atts[error_label] += 1
            except KeyError:
                pass
            vector_atts.append(atts)
    
        return vector_atts
        
    
     
if __name__ == '__main__':
#    filename_input = sys.argv[1]
#    filename_output = sys.argv[2]    
#java -jar LanguageTool.jar -l es /home/elav01/taraxu_data/wmt12/qe/training_set/target_system.spa >  /home/elav01/taraxu_data/wmt12/qe/training_set/target_system.lngt
    filename_input = "/home/elav01/taraxu_data/wmt12/qe/training_set/target_system.lngt"
    filename_output = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.lgt.es.f.jcml"
    existing_jcml = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.jcml"
    LanguageCheckerCmd().offline_process(filename_input, filename_output, existing_jcml)
          
    
    