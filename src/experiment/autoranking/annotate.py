'''
Created on 17 Jan 2012

@author: lefterav
'''



import shutil
import os

#pipeline essentials
from ruffus import *
from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph
import cPickle as pickle

#internal code classes
from experiment.autoranking.bootstrap import cfg
from experiment.autoranking.bootstrap import get_classifier
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

from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator, BerkeleyFeatureGenerator, BerkeleyXMLRPCFeatureGenerator 
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



source_language =  cfg.get("general", "source_language")
target_language =  cfg.get("general", "target_language")

def get_parser(language):
    #this is reading the configuration, maybe move elsewher
    for parser_name in [section for section in cfg.sections() if section.startswith("parser:")]:
        if cfg.get(parser_name, "language") == language:
            tokenize = cfg.getboolean(parser_name, "tokenize")
            if cfg.get(parser_name, "type") == "xmlrpc":
                url = cfg.get(parser_name, "url")
                return BerkeleyXMLRPCFeatureGenerator(url, language, tokenize)
            elif cfg.get(parser_name, "type") == "socket":
                grammarfile = cfg.get(parser_name, "grammarfile")
                berkeley_parser_jar = cfg.get(parser_name, "berkeley_parser_jar")
                py4j_jar = cfg.get(parser_name, "py4j_jar")
                return BerkeleySocketFeatureGenerator(grammarfile, berkeley_parser_jar, py4j_jar, language, tokenize)
    return False
            
#TODO: handle the case where parser is absent for one language

            
@posttask(touch_file("features_berkeley_source.done"))
@active_if(get_parser(source_language))
@transform(data_fetch, suffix(".orig.jcml"), ".parsed.%s.f.jcml" % source_language, source_language, get_parser(source_language))
def features_berkeley_source(input_file, output_file, source_language, parser):
    features_berkeley(input_file, output_file, source_language, parser)

@posttask(touch_file("features_berkeley_target.done"))
@active_if(get_parser(target_language))
@transform(data_fetch, suffix(".orig.jcml"), ".parsed.%s.f.jcml" % target_language, target_language, get_parser(target_language))
def features_berkeley_target(input_file, output_file, target_language, parser):
    features_berkeley(input_file, output_file, source_language, parser)

def features_berkeley(input_file, output_file, language, parser_url, parser):
    saxjcml.run_features_generator(input_file, output_file, [parser])
#    parser = BerkeleyXMLRPCFeatureGenerator(parser_url, language, parser_tokenize)
#    saxjcml.run_features_generator(input_file, output_file, [parser])

#unimplemented



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

@collate([features_berkeley_source, features_berkeley_target], regex(r"([^.]+)\.(.+)\.f.jcml"),  r"\1.all.f.jcml")
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
    pipeline_run([features_gather], multiprocess = 2)