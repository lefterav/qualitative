'''
Created on 17 Jan 2012

@author: lefterav
'''



import shutil
import os

#pipeline essentials
from ruffus import *
from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph, pipeline_printout
import cPickle as pickle

#internal code classes
from experiment.autoranking.bootstrap import cfg
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


path = cfg.get('general','path')
try:
    os.mkdir(path)
except OSError:
    pass
os.chdir(path)
cores = 2

@split(None, "*orig.jcml", cfg.get("annotation", "filenames").split(","))
def data_fetch(input_file, output_files, external_files):
    """
    Fetch training file and place it comfortably in the working directory
    """
    for external_file in external_files:
        print "Moving here external file ", external_file
        (path, setname) = re.findall("(.*)/([^/]+)\.jcml", external_file)[0]
        
        output_file = "%s.%s" % (setname, "orig.jcml")
        shutil.copy(external_file, output_file)


#def features_parse():
#    pass





            
#TODO: handle the case where parser is absent for one language
@split(data_fetch, "*.part.orig.jcml", cores)
def original_data_split(input_files, output_files, parts):
    for input_file in input_files:
        parallelsentences = JcmlReader(input_file).get_parallelsentences()
        length = len(parallelsentences)
        step = len(parallelsentences)/parts
        partindex = 0 
        for index in range(0, length, step):
            partindex += 1
            start = index
            end = index + step - 1
            if (index + (2*step) > length):
                end = length - 1
            try:
                filename_prefix = re.findall("([^.]*)\.orig.jcml", input_file)[0]
                filename = "%s.%d.part.orig.jcml" % (filename_prefix, partindex)
                Parallelsentence2Jcml(parallelsentences[start:end]).write_to_file(filename)
            except IndexError:
                print "Please try to not have a dot in the test set name, cause you don't help me with splitting"
            


source_language =  cfg.get("general", "source_language")
target_language =  cfg.get("general", "target_language")
       
@active_if(cfg.exists_parser(source_language))
@transform(original_data_split, suffix("part.orig.jcml"), "part.parsed.%s.f.jcml" % source_language, source_language, cfg.get_parser_name(source_language))
def features_berkeley_source(input_file, output_file, source_language, source_parser, parser_name):
    features_berkeley(input_file, output_file, source_language)
    
@active_if(cfg.exists_parser(target_language))
@transform(original_data_split, suffix("part.orig.jcml"), "part.parsed.%s.f.jcml" % target_language, target_language, cfg.get_parser_name(target_language))
def features_berkeley_target(input_file, output_file, target_language, parser_name):
    features_berkeley(input_file, output_file, target_language)

def features_berkeley(input_file, output_file, language):
    parser = cfg.get_parser(language) #this is bypassing the architecture, but avoids wasting memory for the loaded parser
    saxjcml.run_features_generator(input_file, output_file, [parser])
    
#    parser = BerkeleyXMLRPCFeatureGenerator(parser_url, language, parser_tokenize)
#    saxjcml.run_features_generator(input_file, output_file, [parser])

#unimplemented


@collate([features_berkeley_source, features_berkeley_target], regex(r"([^.]+)\.(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
def merge_parse_parts(inputs, output):
    parallelsentences = []
    for input in inputs:
        parallelsentences.extend(JcmlReader(input).get_parallelsentences())
    Parallelsentence2Jcml(parallelsentences).write_to_file(output)    


#TODO: probably establish sth like ExternalProcessor object and wrap all these params there
source_language = cfg.get("general", "source_language")
target_language = cfg.get("general", "target_language")
lm_source = False
lm_target = False
for lm_name in [section for section in cfg.sections() if section.startswith("lmserver:")]:
    if cfg.get(lm_name, "language") == source_language:
        lm_source = lm_name
        lm_source_url = cfg.get(lm_source, "url")
        lm_source_tokenize = cfg.getboolean(lm_source, "tokenize")
        lm_source_lowercase = cfg.getboolean(lm_source, "lowercase")
    elif cfg.get(lm_name, "language") == target_language:
        lm_target = lm_name
        lm_target_url = cfg.get(lm_target, "url")
        lm_target_tokenize = cfg.getboolean(lm_target, "tokenize")
        lm_target_lowercase = cfg.getboolean(lm_target, "lowercase")

@active_if(lm_source)
@transform(data_fetch, suffix(".orig.jcml"), ".lm.%s.f.jcml" % source_language, source_language, lm_source_url, lm_source_tokenize, lm_source_lowercase) 
def features_lm_source(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    features_lm(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase)
    #saxjcml.run_features_generator(input_file, output_file, [srilm_ngram])

@active_if(lm_target)
@transform(data_fetch, suffix(".orig.jcml"), ".lm.%s.f.jcml" % target_language, target_language, lm_target_url, lm_target_tokenize, lm_target_lowercase) 
def features_lm_target(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    features_lm(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase)
    
def features_lm(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    features_lm_batch(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase)

def features_lm_batch(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    srilm_ngram = SRILMngramGenerator(lm_url, language, lm_lowercase, lm_tokenize) 
    processed_parallelsentences = srilm_ngram.add_features_batch(JcmlReader(input_file).get_parallelsentences())
    Parallelsentence2Jcml(processed_parallelsentences).write_to_file(output_file)

@active_if(False)
def features_ibm(input_file, output_file, ibm1lexicon):
    ibmfeaturegenerator = Ibm1FeatureGenerator(ibm1lexicon)
    saxjcml.run_features_generator(input_file, output_file, [ibmfeaturegenerator])
    
#unimplemented
def features_lm_single(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    pass

@collate([merge_parse_parts], regex(r"([^.]+)\.(.+)\.f.jcml"),  r"\1.all.f.jcml")
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
    
    pipeline_run([features_gather], multiprocess = cores)