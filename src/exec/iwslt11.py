'''
Created on Sep 12, 2011

@author: elav01
'''
from io.input.linereader import LineReader
from io.output.xmlwriter import XmlWriter
from tara_noorange import Experiment
import os
import sys
import re

if __name__ == '__main__':
    step = int(sys.argv[1])
    mydir = "/share/taraxu/selection-mechanism/iwslt11"
    targetdir = "/share/taraxu/vilar/iwslt11/ibm1/hyps"
    extension = ".hyp"
    
    testset = "iwslt-tst2010"
    pattern_name = "([^/]*)_IWSLT11"
    langpair = "en-fr"
    
    sourcefilename = "/share/taraxu/vilar/iwslt11/data/preproc/devsets/IWSLT11.TALK.tst2010.en-fr.en.fc"
    sourcefilenamename_nopath = re.findall("([^/]*)$", sourcefilename)[0]
    jcmlfilename = "%s/%s.jcml" % (mydir, sourcefilenamename_nopath)
    
    exp = Experiment()
    
    if step == 0:
        
        targetfiles = ["%s/%s" % (targetdir, filename) for filename in os.listdir (targetdir) if filename.endswith(extension)]
        dataset = LineReader(sourcefilename, targetfiles, langpair, testset, pattern_name).get_dataset()
        print "writing"
        XmlWriter(dataset).write_to_file(jcmlfilename)
    
    bpfile_en = jcmlfilename.replace("jcml", "bp.en.jcml")
    if step == 1:
        print "English parser features"
        exp.add_b_features_batch(jcmlfilename, bpfile_en, "http://blade-1.dfki.uni-sb.de:8682", "en")

    bpfile_fr = jcmlfilename.replace("jcml", "bp.fr.jcml")
    if step == 2:
        print "French parser features"
        exp.add_b_features_batch(jcmlfilename, bpfile_fr, "http://blade-1.dfki.uni-sb.de:8683", "fr")
    

    
    
    