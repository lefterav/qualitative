'''
@author: lefterav
'''

import csv
import ConfigParser
import os, errno
import sys

from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from extract_judgments import WMTEvalReader
import fnmatch

if __name__ == '__main__':
        
        langpairs = [
                     ("de", "en"), 
                     ("en", "de"),
                     ("en", "fr"),
                     ("fr", "en"), 
                     ("en", "es"), 
                     ("es", "en"), 
                     ("cs", "en"),  #Caution: for some years, this works with cz. 
                     ("en", "cs"),
                     ("en", "ru"),
                     ("ru", "en"),
                     ("en", "hi"),
                     ("hi", "en")
                    ]
        template_language = ("de", "en")
        path = os.curdir
        
        config_template = "extract_ranking*.%s-%s.cfg" % template_language
        
        
        for (srclang, tgtlang) in langpairs:
            print (srclang, tgtlang)

            
            #get all "year" description files in current directory.
            #if you want only one year, then move the config file to an empty dir and run script from there
            for config_file in os.listdir(path):
                if fnmatch.fnmatch(config_file, config_template):    
            
                    config = ConfigParser.RawConfigParser()
                    sys.stderr.write("Opening config file: %s\n" % config_file)
                    config.read(config_file)
                    
                    new_filename = config_file.replace("extract_ranking", "wmt")
                    new_filename = new_filename.replace("cfg", "jcml")
                    new_filename = new_filename.replace("de-en", "%s-%s" % (srclang, tgtlang))
                    
                    config.set("filters_include", "srclang", srclang)
                    config.set("filters_include", "trglang", tgtlang)
                    
                    try:
                        config.add_section("preprocessing")
                    except:
                        pass
                    config.set("preprocessing", "tokenize_source", "False")
                    config.set("preprocessing", "tokenize_target", "False")
                    config.set("preprocessing", "tokenizer", "/home/elav01/taraxu_tools/moses-scripts/tokenizer.perl")
                    
                    try:
                        os.mkdir("%s-%s" % (srclang, tgtlang))
                    except:
                        pass
                    exact_output_filename = os.path.abspath(os.path.join(os.curdir, "%s-%s" % (srclang, tgtlang), "%s.rank.jcml" % new_filename))
                    #config.set("output", "filename", "/home/elav01/taraxu_data/jcml-latest/raw/%s.rank.jcml" % new_filename)
                    config.set("output", "filename", exact_output_filename)
                    print "File will be written in" , exact_output_filename
                    
                    wmtr = WMTEvalReader(config)
                    parallelsentences = wmtr.parse()
                    if parallelsentences:
                        sys.stderr.write("%d Sentences read, proceeding with writing XML\n" % len(parallelsentences))
                    
                        filename = config.get("output", "filename")
                        xmlwriter = Parallelsentence2Jcml(parallelsentences).write_to_file(filename)
                        sys.stderr.write("Done\n")
                    else:
                        sys.stderr.write("No sentences extracted for language pair\n")
                
