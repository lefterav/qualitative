'''
TaraXU specific script for gathering data of round 2
and wrapping them on a sentence level
Created on Apr 21, 2013

@author: Eleftherios Avramidis

'''

import logging
import os
import fnmatch
from preprocess_glassbox import extract_glassbox_features_moses
import sys


sth = logging.StreamHandler()
sth.setLevel(logging.WARN)




#PATTERNS
if sys.argv[1] == "generic":
    source = "{basepath}/test-data/{set}/*{targetlang}*.{sourcelang}"
    #    testsets = ["wmt11", "openoffice3", "wmt10"]
    testsets = ["wmt11", "wmt10", "openoffice3"]
    #testsets = ["openoffice3"]
    ids = source + ".links"
elif sys.argv[1] == "client":
    source = "/share/taraxu/data/r2-testSets/client/plain/{langpair}/{set}*.txt"
    ids = "{basepath}/test-data/client/raw/{langpair_upper}/{set}*.links"
    testsets = [
"cust_euDE_4",
"Green Fact Sheet_cust_euDE_4",
"ReGen_letak_cust_euDE_4",
"TZ_Way_to_Green.docx_cust_euDE_4",
"069592001_cust1",
"079784001_cust_1",
"069592001_cust_euDE_1",
"079784001_cust_euDE_1",
"351564014_00__2_cust_euDE_2",
"355004004__1_cust_euDE_2",
"35500410402__2_cust_euDE_2",
"069592001_cust_1.",
"079784001_cust_1",
"Change_Tyres_cust_euDE_3",
"ELEVATORS_cust_euDE_4",
"ESCALATORS AND MOVING WALKWAYS_cust_euDE_4",
"Future_tyre_Labelling_cust_euDE_3",
"GEN_cust_euDE_4",
"Oct_cust_euDE_4",
"SAFETY FOR ALL_cust_euDE_4",
"SERVICE EXCELLENCE_cust_euDE_4",
"THE WAY TO GREEN_cust_euDE_4",
"THE_WAY_TO_GREEN_cust_euDE_4",
"SERVICE_EXCELLENCE_cust_euDE_4",
"SAFETY_FOR_ALL_cust_euDE_4",
"ESCALATORS_AND_MOVING_WALKWAYS_cust_euDE_4",
"351564011_00__2_cust_euDE_2",
"351564101_03__02_cust_euDE_2",
"351700050_04__2_cust_euDE_2",
"351750600_2_cust_euDE_2",
"355004001__1_cust_euDE_2",
"355004101_01__2_cust_euDE_2",
"355006001__1_cust_euDE_2"]

target = "{basepath}/system-outputs/{system}/{langpair}/*{set}*"
log = "{basepath}/logs/{langpair}/{system}/*{set}*"

output = "/share/taraxu/selection-mechanism/errorprediction/preprocessing/combined/{set}.{langpair}.{system}.jcml"
 
params = {"basepath":"/share/taraxu/evaluation-rounds/r2"}

backoff_reference = True
try:
    if "--hjersoncounts" in sys.argv[1:]:
        logging.warn("Counting total errors per sentence")
        hjersoncounts = True                
        output = output.replace(".jcml", ".counts.jcml")
        
    if "--noreference" in sys.argv[1:]:
        logging.warn("Disabled reference substitution")
        backoff_reference = False
        output = output.replace(".jcml", ".noref.jcml")
except:
    pass


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
        logging.debug("{set} of {langpair} by {system} not found".format(**params))
	logging.debug("pattern {} in directory {}".format(basename_pattern, directory))

        return None
    return os.path.join(directory,filename)


counter = 0
                

if __name__ == '__main__':
    
    for system in systems:
        for sourcelang, targetlang in langpairs:
	    counter_langpair = 0
            for testset in testsets:
                params["set"] = testset
                params["system"] = system
                params["sourcelang"] = sourcelang
                params["targetlang"] = targetlang
                params["langpair"] = "{sourcelang}-{targetlang}".format(**params)
                params["langpair_upper"] = params["langpair"].upper()
                
                source_filename = _find_filename(source, params)
		ids_filename = _find_filename(ids, params)
                
                target_filename = _find_filename(target, params)
                log_filename = _find_filename(log,params)
                if not log_filename or not source_filename or not ids_filename or not target_filename:
                    continue

                
                output_filename = output.format(**params)
                
                print (source_filename,
                       ids_filename,
                       target_filename,
                       log_filename,
                       output_filename
                       )
                counter+=1
                counter_langpair+=1
                if not "--testlist" in sys.argv:
                    extract_glassbox_features_moses(source_filename, ids_filename, testset, target_filename, log_filename, output_filename, sourcelang, targetlang, backoff_reference, hjersoncounts)
            logging.warn("{}-{}-{}".format(sourcelang, targetlang, counter_langpair))
         
logging.warn("Located {} filename tuples".format(counter)) 
