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

source = "{basepath}/test-data/{set}/*{targetlang}*.{sourcelang}"
ids = "{basepath}/test-data/{set}/*{targetlang}*.{sourcelang}.links"
target = "{basepath}/system-outputs/{system}/{langpair}/*{set}*"
log = "{basepath}/logs/{langpair}/{system}/wmt11.*"

output = "/share/taraxu/selection_mechanism/errorprediction/preprocessing/{set}-{langpair}{system}.jcml"
 
params = {"basepath":"/share/taraxu/evaluation-rounds/r2"}
testsets = ["wmt11", "openoffice3"]
systems = ["moses"]
langpairs = [('de','en'),('en','de'),('de','fr'),('fr','de'),('de','es'),('es','de')]

def _find_filename(fullpattern, params):
    #this needs fnmatch substitution
    filepattern = fullpattern.format(**params)
    directory, basename_pattern = os.path.split(filepattern)
    try:
        dir_files = os.listdir(directory)
        filename = fnmatch.filter(dir_files, basename_pattern).pop()
    except:
        logging.warn("{set} of {langpair} by {system} not found".format(**params))
	logging.warn("pattern {} in directory {}".format(basename_pattern, directory))

        return None
    return os.path.join(directory,filename)
            
                

if __name__ == '__main__':
    
    for system in systems:
        for sourcelang, targetlang in langpairs:
            for testset in testsets:
                params["set"] = testset
                params["system"] = system
                params["sourcelang"] = sourcelang
                params["targetlang"] = targetlang
                params["langpair"] = "{sourcelang}-{targetlang}".format(**params)
                
                source_filename = _find_filename(source, params)
		ids_filename = _find_filename(ids, params)
                
                target_filename = _find_filename(target, params)
                log_filename = _find_filename(log,params)
                if not log_filename:
                    continue

                
                output_filename = output.format(**params)
                
                print (source_filename,
                       ids_filename,
                       target_filename,
                       log_filename,
                       output_filename
                       )
                                
#                extract_glassbox_features_moses(source_filename, ids_filename, testset, target_filename, log_filename, output_filename, sourcelang, targetlang)
