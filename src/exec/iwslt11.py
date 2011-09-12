'''
Created on Sep 12, 2011

@author: elav01
'''
from io.input.linereader import LineReader
from io.output.xmlwriter import XmlWriter
import os
import sys
import re

if __name__ == '__main__':
    step = sys.argv[0]
    mydir = "/share/taraxu/selection-mechanism/iwslt11"
    
    
    if step == 0:
        
        sourcefile = "/share/taraxu/vilar/iwslt11/data/preproc/devsets/IWSLT11.TALK.tst2010.en-fr.en.fc"
        targetdir = "/share/taraxu/vilar/iwslt11/ibm1/hyps"
        extension = ".hyp"
        
        testset = "iwslt-tst2010"
        pattern_name = "([^/]*)_IWSLT11"
        langpair = "en-fr"
        
        sourcefilename_nopath = re.findall("([^/]*)$")[0]
        
        jcmlfilename = "%s/%s.jcml" % (mydir, sourcefilename_nopath)
        
        targetfiles = [filename for filename in os.listdir (targetdir) if filename.endswith(extension)]
        dataset = LineReader(sourcefile, targetfiles, langpair, testset, pattern_name).get_dataset()
        print "writing"
        XmlWriter(dataset).write_to_file(jcmlfilename)
    
    
    
    
    
    