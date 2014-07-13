'''
Created on Sep 12, 2011

@author: Eleftherios Avramidis
'''
from io_utils.input.linereader import LineReader
from io_utils.input.jcmlreader import JcmlReader
from io_utils.output.xmlwriter import XmlWriter
from tara_noorange import Experiment
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
import os
import sys
import re

if __name__ == '__main__':
    step_start = int(sys.argv[2])
    step_end = int(sys.argv[3])
    mydir = "/home/Eleftherios Avramidis/iwslt11/test-combo"
    #mydir = "/share/taraxu/selection-mechanism/iwslt11/"
    targetdir = "/home/Eleftherios Avramidis/iwslt11/test-combo"
    extension = ".txt.fc"
    
    testset = "iwslt-tst2011-combo"
    pattern_name = "tst2011.MT_EF.system([0-9]*)"
    langpair = "en-fr"
    
    sourcefilename = sys.argv[1] 
    #"/share/taraxu/vilar/iwslt11/data/preproc/devsets/IWSLT11.TALK.tst2010.en-fr.en.fc"
    sourcefilenamename_nopath = re.findall("([^/]*)$", sourcefilename)[0]
    print  "Filename:", sourcefilenamename_nopath
    if not sourcefilenamename_nopath.endswith(".jcml"):
        jcmlfilename = "%s/%s.jcml" % (mydir, sourcefilenamename_nopath)
    else:
        jcmlfilename = sourcefilename
    
    exp = Experiment()
    
    for step in range (step_start, step_end + 1):
        if step == 0:
            
            targetfiles = ["%s/%s" % (targetdir, filename) for filename in os.listdir (targetdir) if filename.endswith(extension)]
            dataset = LineReader(sourcefilename, targetfiles, langpair, testset, pattern_name).get_dataset()
            print "writing"
            XmlWriter(dataset).write_to_file(jcmlfilename)
        
        bpfile_en = jcmlfilename.replace(".jcml", ".bp.en.jcml")
        if step == 10:
            print "English parser features"
            exp.add_b_features_batch(jcmlfilename, bpfile_en, "http://percival.sb.dfki.de:8682", "en")
    
        bpfile_fr = jcmlfilename.replace(".jcml", ".bp.fr.jcml")
        if step == 20:
            print "French parser features"
            exp.add_b_features_batch(jcmlfilename, bpfile_fr, "http://percival.sb.dfki.de:8683", "fr")
            
        lmfile_fr = jcmlfilename.replace(".jcml", ".lm.fr.jcml") 
        if step == 30:
            print "French LM features"
            freqcase_file = "/share/taraxu/vilar/iwslt11/data/preproc/un.en-fr/training.fr"
            exp.add_ngram_features_batch(jcmlfilename, lmfile_fr, "http://percival.sb.dfki.de:8585", "fr", None, False, freqcase_file)
        lmfile_en = jcmlfilename.replace(".jcml", ".lm.en.jcml")
        if step == 40:
            print "English LM features"
            exp.add_ngram_features_batch(jcmlfilename, lmfile_en, "http://percival.sb.dfki.de:8584", "en")
        ibm1file = jcmlfilename.replace(".jcml", ".ibm.jcml")
        if step == 50:
            print "IBM Model 1 features"
            ibm1lexicon = "/share/taraxu/vilar/iwslt11/ibm1/parallel-TED.tags.lexicon"
            dataset = JcmlReader(jcmlfilename).get_dataset()
            dataset = Ibm1FeatureGenerator(ibm1lexicon).add_features_dataset(dataset)
            XmlWriter(dataset).write_to_file(ibm1file)
        merged_jcml = jcmlfilename.replace(".jcml", ".ef.jcml")
        if step == 100:
            print "Getting things together"
            tobermerged = [bpfile_en, bpfile_fr, lmfile_fr, lmfile_en, ibm1file]
            original_file = tobermerged[0]
            original_dataset = JcmlReader(original_file).get_dataset()
            for appended_file in tobermerged[1:]:
                appended_dataset = JcmlReader(appended_file).get_dataset()
                original_dataset.merge_dataset_symmetrical(appended_dataset)
            XmlWriter(original_dataset).write_to_file(merged_jcml)
                
        exfile = jcmlfilename.replace(".jcml", ".if.jcml")
        if step == 110:
            print "final features"
            
            exp.analyze_external_features(merged_jcml, exfile, ("en", "fr")) 
print "Done!" 

    
    
