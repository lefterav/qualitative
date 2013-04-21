'''
Created on Apr 21, 2013

@author: Eleftherios Avramidis

'''

import logging
import os
import fnmatch
from preprocess_glassbox import extract_glassbox_features_moses


sth = logging.StreamHandler()
sth.setLevel(logging.DEBUG)

source = "{basepath}/test-data/{set}/{set}.*{targetlang}.{sourcelang}"
ids = "{basepath}/r2/test-data/{set}/{set}.*{targetlang}.{sourcelang}.links"
target = "{basepath}/system-outputs/{system}/{langpair}/*{set}*"
log = "{basepath}/logs/{langpair}/{system}/wmt11.*"

output = "/share/taraxu/selection_mechanism/errorprediction/preprocessing/{set}-{langpair}{system}.jcml"
 
params = {"basepath":"/share/taraxu/evaluation-rounds/r2/"}
testsets = ["wmt11"]
systems = ["moses"]
langpairs = [('de','en')]

def _find_filename(fullpattern, params):
    #this needs fnmatch substitution
    filepattern = fullpattern.format(**params)
    directory, basename_pattern = os.path.split(filepattern)
    dir_files = os.listdir(directory)
    filename = fnmatch.filter(dir_files, basename_pattern).pop()
    return filename
            
                

if __name__ == '__main__':
    
    for system in systems:
        for sourcelang, targetlang in langpairs:
            for testset in testsets:
                params["set"] = testset
                params["system"] = system
                params["sourcelang"] = sourcelang
                params["targetlang"] = targetlang
                params["langpair"] = "{sourcelang}-{targetlang}".format(**params)
                
                source_filename = source.format(**params)
                ids_filename = ids.format(**params)
                
                target_filename = _find_filename(target, params)
                log_filename = _find_filename(log,params)
                
                output_filename = output.format(**params)
                
                print (source_filename,
                       ids_filename,
                       target_filename,
                       log_filename,
                       output_filename
                       )
                                
#                extract_glassbox_features_moses(source_filename, ids_filename, testset, target_filename, log_filename, output_filename, sourcelang, targetlang)
