'''
Created on 30 Jun 2014

This is for bunching together many text files (i.e. many system outputs) without given features for each of them.

@author: lefterav
'''
import argparse
from sentence.sentence import SimpleSentence
from collections import OrderedDict
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from featuregenerator.glassbox.moses.extractor import MosesGlassboxExtractor

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert txt files into jcml')
    parser.add_argument("-s", "--source", dest="source_filename",
                      help="read one source sentence per line from FILE", metavar="FILE")
    
    parser.add_argument("-t", "--translations", dest="target_filenames",
                      help="read one translation output sentence per line from FILE", metavar="FILE", nargs="+")
    
    parser.add_argument("-m", "--systems", dest="system_names",
                      help="system name", nargs="+")
    
  
    parser.add_argument("-r", "--reference", dest="reference_filename",
                      help="read one reference sentence per line from FILE", metavar="FILE")
    
    parser.add_argument("-l", "--score", dest="score_filename",
                      help="read one score per line from FILE", metavar="FILE")
    
    parser.add_argument("-a", "--feature-names", action="append", dest="feature_names", 
                      help="a list of feature names", nargs='?')
    
    parser.add_argument("-q", "--feature-files", action="append", dest="feature_files",  default=[],
                      help="a list of feature FILEs in respective order")

    parser.add_argument("-b", "--target-features-tab", dest="target_features_tab", 
                      help="all target features in one file, tab-separated")
    
    parser.add_argument("-n", "--target-features-tab-names", dest="target_features_tab_names", 
                      help="all target feature names in one file, tab-separated")

    
    parser.add_argument("-o", "--output", dest="output_filename",
                      help="write output to this jcml FILE", metavar="FILE")
    
    parser.add_argument("-f", "--langsrc", dest="langsrc",
                      help="source language code")
    
    parser.add_argument("-e", "--langtgt", dest="langtgt",
                      help="target language code")
    
    parser.add_argument("-u", "--testset", dest="testset",
                      help="set name")
    
    parser.add_argument("-g", "--moseslog", dest="moseslog",
                      help="verbose log of moses decoding")
    
    args = parser.parse_args()
    
    source_file = open(args.source_filename, 'r')
    target_files = [open(target_filename, 'r') for target_filename in args.target_filenames]
    
    feature_file_objects = [open(f, 'r') for f in args.feature_files]
    print args.feature_files, args.feature_names
    try:
        reference_file = open(args.reference_filename, 'r')
    except:
        reference_file = None
    try:
        score_file = open(args.score_filename)
    except:
        score_file = None
        
    try:
        target_features_tabfile = open(args.target_features_tab)
    except:
        target_features_tabfile = None
    
    try:
        target_features_tab_names_file = open(args.target_features_tab_names)
        target_features_tab_names = target_features_tab_names_file.readline().strip().split("\t")
        target_features_tab_names_file.close()
    except:
        target_features_tab_names = []
#    print "Feature tab names", target_features_tab_names 
    
    if args.moseslog:
        extractor = MosesGlassboxExtractor()
        glassbox_features_dicts = extractor.create_dicts_of_sentences_attributes(args.moseslog)

    parallelsentences = []
    i = 0
    
    for source_line in source_file:
        i+=1
        atts = OrderedDict()
        source_line = source_line.strip()
        target_sentences = []
        for target_file, system in zip(target_files, args.system_names):
            target_line = target_file.readline().strip()
            atts["system"] = system
        
            if reference_file:
                reference_line = reference_file.readline().strip()
                reference_sentence = SimpleSentence(reference_line)
            else:
                reference_sentence = None
            
            #target sentence features        
            if score_file:
                score = score_file.readline().strip()
                atts["score"] = score
            

            
            #process glass-box features
            if args.moseslog:
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
                
            target_sentences.append(SimpleSentence(target_line, atts))
            
        source_sentence = SimpleSentence(source_line)
        
        additional_atts = {}
        
        if args.feature_names and feature_file_objects:
            for feature_name, file_object in zip(args.feature_names, feature_file_objects):
                value = file_object.readline().strip()
                additional_atts[feature_name] = value
            
                
        ps_atts =  {"langsrc" : args.langsrc ,
                     "langtgt" : args.langtgt ,
                     "testset" : args.testset ,
                     "id" : str(i)}
        
        ps_atts.update(additional_atts)
        
        ps = ParallelSentence(source_sentence, target_sentences, reference_sentence, ps_atts)
        parallelsentences.append(ps)
    
    for file_object in feature_file_objects:
        file_object.close()
    
    for target_file in target_files:
        target_file.close()
    
    Parallelsentence2Jcml(parallelsentences).write_to_file(args.output_filename)
    
