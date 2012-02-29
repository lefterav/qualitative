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
        pss = JcmlReader(existing_jcml).get_parallelsentences()
        file_input = open(filename_input, 'r')
        file_content = file_input.read()
        att_vector = self._get_att_vector(file_content)
        att_vector.reverse()
        
        new_pss = []
        
        for ps in pss:
            atts = att_vector.pop()
            atts = dict([(k, str(v)) for k,v in atts.iteritems()])
            ps.add_attributes(atts)
        
        Parallelsentence2Jcml(pss).write_to_file(filename_output)
        
                
        
    
    
    def _get_att_vector(self, file_content):
        
        
        pattern = "\d*.\) Line (\d*), column \d*, Rule ID: (.*)\n"
        
        feature_entries = re.findall(pattern, file_content)
        features_entries = [(int(key)-1, value.replace("[", "_").replace("]", "_")) for  (key, value) in feature_entries]
        errors_per_sentence = {}
       
        #first make one list of error ids per sentence 
        for sentence_id , error_id in feature_entries:
            try:
                errors_per_sentence[int(sentence_id)-1].append(error_id)
            except KeyError:
                errors_per_sentence[int(sentence_id)-1] = [error_id]
        
        
        #construct a vector of dictionaries with counts
        vector_atts = []
        for i in range(0, max(errors_per_sentence.keys())+1):
            atts = {}
            try:
                for error_id in errors_per_sentence[i]:
                    error_id = "tgt-1_lgt_{0}".format(error_id)
                    try:
                        atts[error_id] += 1
                    except KeyError:
                        atts[error_id] = 1
                    vector_atts.append(atts)
            except KeyError:
                vector_atts.append({})
    
        return vector_atts
        
    
     
if __name__ == '__main__':
#    filename_input = sys.argv[1]
#    filename_output = sys.argv[2]    
#java -jar LanguageTool.jar -l es /home/elav01/taraxu_data/wmt12/qe/training_set/target_system.spa >  /home/elav01/taraxu_data/wmt12/qe/training_set/target_system.lngt
    filename_input = "/home/elav01/taraxu_data/wmt12/qe/training_set/target_system.lngt"
    filename_output = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.lgt.es.f.jcml"
    existing_jcml = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.jcml"
    LanguageCheckerCmd().offline_process(filename_input, filename_output, existing_jcml)
          
    
    