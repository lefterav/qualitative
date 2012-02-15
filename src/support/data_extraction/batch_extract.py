'''
@author: lefterav
'''

import csv
import ConfigParser
import os, errno
import sys

from io.sax.saxps2jcml import Parallelsentence2Jcml
from extract_judgments import WMTEvalReader
import fnmatch

if __name__ == '__main__':
        
        langpairs = [("de", "en"), ("en", "de"), ("en", "fr"), ("fr", "en"), ("en", "es"), ("es", "en"), ("cz", "en"), ("en", "cz")]
        template_language = ("de", "en")
        path = os.curdir
        
        config_template = "extract_ranking*.%s-%s.cfg" % template_language
        
        
        for (srclang, tgtlang) in langpairs:
            print (srclang, tgtlang)

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
                    


                    
                    config.set("output", "filename", "/home/elav01/taraxu_data/jcml-latest/%s.rank.jcml" % new_filename)
                    
                    
                    wmtr = WMTEvalReader(config)
                    parallelsentences = wmtr.parse()
                    
                    sys.stderr.write("%d Sentences read, proceeding with writing XML\n" % len(parallelsentences))
 
                    filename = config.get("output", "filename")
                    xmlwriter = Parallelsentence2Jcml(parallelsentences).write_to_file(filename)
                    sys.stderr.write("Done\n")
                