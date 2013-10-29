'''
Created on 23 Feb 2012

@author: lefterav
'''
from optparse import OptionParser
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from featuregenerator.glassbox.moses.extractor import MosesGlassboxExtractor
from collections import OrderedDict

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source_filename",
                      help="read one source sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-t", "--translation", nargs=4,  dest="target_filenames", type="str",
                      help="read one translation output sentence per line from FILE s", metavar="FILE")
    
    parser.add_option("-m", "--systems", nargs=4,  dest="system_names",
                      help="system names")    
  
    parser.add_option("-r", "--reference", dest="reference_filename",
                      help="read one reference sentence per line from FILE", metavar="FILE")
    
    parser.add_option("-l", "--scores", nargs=4, dest="score_filenames",
                      help="read one score per line from FILE", metavar="FILE")
    
    parser.add_option("-a", "--feature-names", nargs=17,  dest="feature_names", type="str",
                      help="a list of feature names", default=[])
                      
    parser.add_option("-v", "--target-features-csv", nargs=4,  dest="target_feature_csv_files",
                      help="a list of CSV files containing system features, one file per system output")

    
    parser.add_option("-q", "--feature-files", nargs=4,  dest="feature_files", type="str", default=[],
                      help="a list of feature FILEs in respective order")
    
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
    
    print opt.target_filenames
    print opt.system_names
    
    target_files = [open(target_filename, 'r') for target_filename in opt.target_filenames] 
    
    feature_file_objects = [open(f, 'r') for f in opt.feature_files]
    print opt.target_feature_csv_files, opt.feature_names
    try:
        reference_file = open(opt.reference_filename, 'r')
    except:
        reference_file = None
    try:
        score_files = [open(score_filename) for score_filename in opt.score_filenames]
    except:
        score_files = None
    
    if opt.moseslog:
        extractor = MosesGlassboxExtractor()
        glassbox_features_dicts = extractor.create_dicts_of_sentences_attributes(opt.moseslog)
    
    if opt.target_feature_csv_files:
        target_feature_csv_files = dict([(sys_name,open(feature_filename)) for sys_name, feature_filename in zip(opt.system_names,opt.target_feature_csv_files)])
    else:
        target_feature_csv_files = None
    

    parallelsentences = []
    i = 0
    
    for source_line in source_file:
        i+=1
        atts = OrderedDict()
        source_line = source_line.strip()
        
        if reference_file:
            reference_line = reference_file.readline().strip()
            reference_sentence = SimpleSentence(reference_line)
        else:
            reference_sentence = None
        
        if score_files:
            scores = dict([(system_name, float(score_file.readline().strip())) for score_file, system_name in zip(score_files, opt.system_names)])
        
        #TODO: won't work after number of target sentences changed. look at older version
        if opt.moseslog:
            atts.update(glassbox_features_dicts[i-1])
        
        source_sentence = SimpleSentence(source_line)
        
        target_sentences = []
        
        #prepare target sentences
        for target_file, system_name in zip(target_files, opt.system_names):
           atts = {}
           atts["system"] = system_name
           
           if score_files:
               atts["rank"] = scores[system_name]
           if target_feature_csv_files:
               features = zip(opt.feature_names, target_feature_csv_files[system_name].readline().strip().split(","))
               atts.update(features)
               
           
    	   target_line = target_file.readline().strip()
           target_sentences.append(SimpleSentence(target_line, atts))
    
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
    
