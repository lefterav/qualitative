'''
Created on 17 Jan 2012

@author: lefterav
'''



import shutil
import os
import math

#pipeline essentials
from ruffus import *
from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph, pipeline_printout
import cPickle as pickle

#internal code classes
from bootstrap import cfg
from io.input.orangereader import OrangeData
from io.sax.saxjcml2orange import SaxJcml2Orange
from io.input.jcmlreader import JcmlReader
from io.sax import saxjcml2orange
from io.sax.saxps2jcml import Parallelsentence2Jcml 
from sentence.dataset import DataSet
from sentence.rankhandler import RankHandler
from featuregenerator.diff_generator import DiffGenerator
from sentence.scoring import Scoring

from io import saxjcml


#ML
from orange import ExampleTable
import orange
from xml import sax

import re

from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
from featuregenerator.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
from featuregenerator.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.bleu.bleugenerator import BleuGenerator
from featuregenerator.attribute_rank import AttributeRankGenerator
from io.input.xmlreader import XmlReader


cores = 2
parallel_feature_functions = []


path = cfg.get_path()
os.chdir(path)
source_language =  cfg.get("general", "source_language")
target_language =  cfg.get("general", "target_language")
training_sets = cfg.get("training", "filenames").split(",")
testing_set = cfg.get("testing", "filename")
all_sets = training_sets
#all_sets.append(testing_set)

print all_sets

@split(None, "*orig.jcml", all_sets)
def data_fetch(input_file, output_files, external_files):
    """
    Fetch training file and place it comfortably in the working directory
    Files are expected to contain the set name, followed by the ending .jcml
    """
    for external_file in external_files:
        print "Moving here external file ", external_file
        basename = re.findall("(.*).jcml", os.path.basename(external_file))[0]
        basename = basename.replace(".", "-")
        
        output_file = "{0}.{1}".format(basename, "orig.jcml")
        shutil.copy(external_file, output_file)
        
            
@split(data_fetch, "*.part.jcml", cores)
def original_data_split(input_files, output_files, parts):
    """
    Split the datasets to parts, in order to perform heavy tasks
    """
    for input_file in input_files:
        print "splitting file", input_file
        re_split = "([^.]*)\.orig\.(jcml)"
        XmlReader(input_file).split_and_write(parts, re_split)


       
@active_if(cfg.exists_parser(source_language))
@transform(original_data_split, suffix("part.jcml"), "part.parsed.%s.f.jcml" % source_language, source_language, cfg.get_parser_name(source_language))
def features_berkeley_source(input_file, output_file, source_language, source_parser, parser_name):
    features_berkeley(input_file, output_file, source_language)
    
@active_if(cfg.exists_parser(target_language))
@transform(original_data_split, suffix("part.jcml"), "part.parsed.%s.f.jcml" % target_language, target_language, cfg.get_parser_name(target_language))
def features_berkeley_target(input_file, output_file, target_language, parser_name):
    features_berkeley(input_file, output_file, target_language)

def features_berkeley(input_file, output_file, language):
    """
    Parsing
    """
    parser = cfg.get_parser(language) #this is bypassing the architecture, but avoids wasting memory for the loaded parser
    saxjcml.run_features_generator(input_file, output_file, [parser])
    
#    parser = BerkeleyXMLRPCFeatureGenerator(parser_url, language, parser_tokenize)
#    saxjcml.run_features_generator(input_file, output_file, [parser])

#@collate(features_berkeley_source, regex(r"([^.]+)\.(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
@active_if(cfg.exists_parser(source_language))
@merge(features_berkeley_source, "parsed.%s.f.jcml" % source_language)
def merge_parse_parts_source(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(source_language)):
    parallel_feature_functions.append(merge_parse_parts_source)

@active_if(cfg.exists_parser(target_language))
@merge(features_berkeley_target, "parsed.%s.f.jcml" % target_language)
def merge_parse_parts_target(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(target_language)):
    parallel_feature_functions.append(merge_parse_parts_target)


def merge_parts(inputs, output):
    parallelsentences = []
    for input in inputs:
        parallelsentences.extend(JcmlReader(input).get_parallelsentences())
    Parallelsentence2Jcml(parallelsentences).write_to_file(output)    


@active_if(cfg.exists_lm(source_language))
@transform(data_fetch, suffix(".orig.jcml"), ".lm.%s.f.jcml" % source_language, source_language, cfg.get_lm_name(source_language)) 
def features_lm_source(input_file, output_file, language, lm_name):
    features_lm(input_file, output_file, language, lm_name)
    #saxjcml.run_features_generator(input_file, output_file, [srilm_ngram])
if (cfg.exists_lm(source_language)):
    parallel_feature_functions.append(features_lm_source)

@active_if(cfg.exists_lm(target_language))
@transform(data_fetch, suffix(".orig.jcml"), ".lm.%s.f.jcml" % target_language, target_language, cfg.get_lm_name(target_language)) 
def features_lm_target(input_file, output_file, language, lm_name):
    features_lm(input_file, output_file, language, lm_name)
if (cfg.exists_lm(target_language)):
    parallel_feature_functions.append(features_lm_source)
    
def features_lm(input_file, output_file, language, lm_name):
    features_lm_batch(input_file, output_file, language, lm_name)

def features_lm_batch(input_file, output_file, language, lm_name):
    srilmgenerator = cfg.get_lm(language) 
    processed_parallelsentences = srilmgenerator.add_features_batch(JcmlReader(input_file).get_parallelsentences())
    Parallelsentence2Jcml(processed_parallelsentences).write_to_file(output_file)

#unimplemented
def features_lm_single(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    pass

@active_if(cfg.exists_checker(source_language))
@transform(data_fetch, suffix(".orig.jcml"), ".iq.%s.f.jcml" % source_language, target_language,)
def features_checker_source(input_file, output_file, language):
    features_checker(input_file, output_file, language)
if cfg.exists_checker(source_language):
    parallel_feature_functions.append(features_checker_source)

@active_if(cfg.exists_checker(target_language))
@transform(data_fetch, suffix(".orig.jcml"), ".iq.%s.f.jcml" % target_language, target_language)
def features_checker_target(input_file, output_file, language):
    features_checker(input_file, output_file, language)
if cfg.exists_checker(target_language):
    parallel_feature_functions.append(features_checker_target)

def features_checker(input_file, output_file, language):
    language_checker = cfg.get_checker(language)
    saxjcml.run_features_generator(input_file, output_file, [language_checker])



@active_if(False)
def features_ibm(input_file, output_file, ibm1lexicon):
    ibmfeaturegenerator = Ibm1FeatureGenerator(ibm1lexicon)
    saxjcml.run_features_generator(input_file, output_file, [ibmfeaturegenerator])
    


#active_parallel_feature_functions = [function for function in parallel_feature_functions if function.is_active]

#first part of the regular expression is the basename of the dataset
@collate(parallel_feature_functions, regex(r"([^.]+)\.(.+)\.f.jcml"),  r"\1.all.f.jcml")
def features_gather(singledataset_annotations, gathered_singledataset_annotations):
    tobermerged = singledataset_annotations
    original_file = tobermerged[0]
    original_dataset = JcmlReader(original_file).get_dataset()
    for appended_file in tobermerged[1:]:
        appended_dataset = JcmlReader(appended_file).get_dataset()
        original_dataset.merge_dataset_symmetrical(appended_dataset)
    Parallelsentence2Jcml(original_dataset.get_parallelsentences()).write_to_file(gathered_singledataset_annotations)

    
@transform(features_gather, suffix(".all.f.jcml"), ".all.analyzed.f.jcml", cfg.get("general", "source_language"), cfg.get("general", "target_language"))    
def analyze_external_features(input_file, output_file, source_language, target_language):
    langpair = (source_language, target_language)
    analyzers = [LengthFeatureGenerator(),
                 ParserMatches(langpair),
                 RatioGenerator()]
    saxjcml.run_features_generator(input_file, output_file, analyzers)
    

@active_if(cfg.getboolean("annotation", "reference_features"))
@transform(data_fetch, suffix(".orig.jcml"), ".ref.f.jcml", cfg.get("annotation", "moreisbetter").split(","), cfg.get("annotation", "lessisbetter").split(",")) 
def reference_features(input_file, output_file, moreisbetter_atts, lessisbetter_atts):
    analyzers = [LevenshteinGenerator(),
                 BleuGenerator(),
                 RatioGenerator()
                 ]
    
    for attribute in moreisbetter_atts:
        analyzers.append(AttributeRankGenerator(attribute), None, True)
    for attribute in lessisbetter_atts:
        analyzers.append(AttributeRankGenerator(attribute))
        
    saxjcml.run_features_generator(input_file, output_file, analyzers)



def create_ranks():
    pass



if __name__ == '__main__':
    
    
    pipeline_printout_graph("flowchart.pdf", "pdf", [features_gather])
    import sys
    
    pipeline_run([analyze_external_features], multiprocess = cores)
    #pipeline_run([original_data_split], multiprocess = 2)