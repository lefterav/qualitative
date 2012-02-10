'''
Created on 10 Φεβ 2012

@author: lefterav
'''

import csv
import ConfigParser
import os
import sys

from io.sax.saxps2jcml import Parallelsentence2Jcml
from extract_judgments import WMTEvalReader
import fnmatch

if __name__ == '__main__':
        config = ConfigParser.RawConfigParser()
        
        langpairs = [("de", "en"), ("en", "de"), ("en", "fr"), ("fr", "en"), ("en", "es"), ("es", "en"), ("cz", "en"), ("en", "cz")]
        template_language = ("de", "en")
        path = os.curdir
        
        config_template = "extract_ranking*.%s-%s.cfg" % template_language
        
        for (srclang, tgtlang) in langpairs:
            for config_file in path:
                if fnmatch.fnmatch(config_file, '*.txt'):    
            
                    sys.stderr.write("Opening config file: %s\n" % config_file)
                    config.read(config_file)
                    
                    new_filename = config_file.replace("extract_ranking", "wmt")
                    new_filename = new_filename.replace("cfg", "jcml")
                    
                    config.set("filters_include", "srclang", srclang)
                    config.set("filters_include", "tgtlang", tgtlang)
                    config.set("output", "filename", "/home/elav01/taraxu_data/jcml/%s-%s/%s.%s-%s.rank.jcml" % (srclang, tgtlang, new_filename, srclang, tgtlang))
                    
                    
                    wmtr = WMTEvalReader(config)
                    parallelsentences = wmtr.parse()
                    
                    sys.stderr.write("Sentences read, proceeding with writing XML\n")
 
                    filename = config.get("output", "filename")
                    xmlwriter = Parallelsentence2Jcml(parallelsentences).write_to_file(filename)
                    sys.stderr.write("Done")
                