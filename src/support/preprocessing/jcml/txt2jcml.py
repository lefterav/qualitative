'''
Created on 23 Feb 2012

@author: lefterav
'''
from optparse import OptionParser
from sentence.sentence import SimpleSentence
from collections import OrderedDict
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from featuregenerator.glassbox.moses.extractor import MosesGlassboxExtractor

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source_filename",
                      help="read one source sentence per line from FILE", metavar="FILE")
    
<<<<<<< HEAD
<<<<<<< HEAD
    parser.add_option("-t", "--translation", dest="target_filename",
                      help="read one translation output sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-m", "--sys sbsbtem", dest="system_name",
                      help="system name")
=======
    parser.add_option("-t", "--translation", nargs=4,  dest="target_filenames", type="str",
                      help="read one translation output sentence per line from FILE s", metavar="FILE")
>>>>>>> 908ddf29f668d20056dda86c58b2df2b112c3a17
=======
    parser.add_option("-t", "--translation", dest="target_filename",
                      help="read one translation output sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-m", "--system", dest="system_name",
                      help="system name")
>>>>>>> a7215bd3893b88902636e6c05e0f3c4faa7e30fc
    
  
    parser.add_option("-r", "--reference", dest="reference_filename",
                      help="read one reference sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-l", "--score", dest="score_filename",
                      help="read one score per line from FILE", metavar="FILE")
    
    parser.add_option("-a", "--feature-names", action="append", dest="feature_names", type="str",
                      help="a list of feature names", default=[])
    
<<<<<<< HEAD
<<<<<<< HEAD
        
    parser.add_option("-q", "--feature-files", action="append", dest="feature_files", type="str", default=[],
=======
    parser.add_option("-q", "--feature-files", nargs=4,  dest="feature_files", type="str", default=[],
>>>>>>> 908ddf29f668d20056dda86c58b2df2b112c3a17
=======
    parser.add_option("-q", "--feature-files", action="append", dest="feature_files", type="str", default=[],
>>>>>>> a7215bd3893b88902636e6c05e0f3c4faa7e30fc
                      help="a list of feature FILEs in respective order")

    parser.add_option("-b", "--target-features-tab", dest="target_features_tab", type="str", 
                      help="all target features in one file, tab-separated")
    
    parser.add_option("-n", "--target-features-tab-names", dest="target_features_tab_names", type="str", 
                      help="all target feature names in one file, tab-separated")

    
    parser.add_option("-o", "--output", dest="output_filename",
                      help="write output to this jcml FILE", metavar="FILE")
    
    parser.add_option("-f", "--langsrc", dest="langsrc",
                      help="source language code")
    
    parser.add_option("-e", "--langtgt", dest="langtgt",
                      help="target language code")
    
    parser.add_option("-u", "--testset", dest="testset",
                      help="set name")
    
    parser.add_option("-g", "--moseslog", dest="moseslog",
                      help="verbose log of moses decoding")
    
    (opt, args) = parser.parse_args()
    
    source_file = open(opt.source_filename, 'r')
    target_file = open(opt.target_filename, 'r')
    
    feature_file_objects = [open(f, 'r') for f in opt.feature_files]
    print opt.feature_files, opt.feature_names
    try:
        reference_file = open(opt.reference_filename, 'r')
    except:
        reference_file = None
    try:
        score_file = open(opt.score_filename)
    except:
        score_file = None
        
    try:
        target_features_tabfile = open(opt.target_features_tab)
    except:
        target_features_tabfile = None
    
    try:
        target_features_tab_names_file = open(opt.target_features_tab_names)
        target_features_tab_names = target_features_tab_names_file.readline().strip().split("\t")
        target_features_tab_names_file.close()
    except:
        target_features_tab_names = []
#    print "Feature tab names", target_features_tab_names 
    
    if opt.moseslog:
        extractor = MosesGlassboxExtractor()
        glassbox_features_dicts = extractor.create_dicts_of_sentences_attributes(opt.moseslog)

    parallelsentences = []
    i = 0
    
    for source_line in source_file:
        i+=1
        atts = OrderedDict()
        source_line = source_line.strip()
        target_line = target_file.readline().strip()
        
        
        if reference_file:
            reference_line = reference_file.readline().strip()
            reference_sentence = SimpleSentence(reference_line)
        else:
            reference_sentence = None
        
        #target sentence features        
        if score_file:
            score = score_file.readline().strip()
            atts["score"] = score
        
        atts["system"] = opt.system_name
        
        #process glass-box features
        if opt.moseslog:
            atts.update(glassbox_features_dicts[i-1])
        
        #process tab-separated features file
        if target_features_tabfile:
            feature_values = target_features_tabfile.readline().strip().split("\t")
            for i, feature_value in enumerate(feature_values):
                try:
                    feature_name = target_features_tab_names[i-1]
                except:
                    feature_name = i
                atts["qb_{}".format(feature_name)] = feature_value
                
        source_sentence = SimpleSentence(source_line)
        target_sentences = [SimpleSentence(target_line, atts)]
        
        additional_atts = {}
        for feature_name, file_object in zip(opt.feature_names, feature_file_objects):
            value = file_object.readline().strip()
            additional_atts[feature_name] = value
            
                
        ps_atts =  {"langsrc" : opt.langsrc ,
                     "langtgt" : opt.langtgt ,
                     "testset" : opt.testset ,
                     "id" : str(i)}
        
        ps_atts.update(additional_atts)
        
        ps = ParallelSentence(source_sentence, target_sentences, reference_sentence, ps_atts)
        parallelsentences.append(ps)
    
    for file_object in feature_file_objects:
        file_object.close()
    
    Parallelsentence2Jcml(parallelsentences).write_to_file(opt.output_filename)
    
