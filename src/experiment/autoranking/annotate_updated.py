'''
Created on 17 Jan 2012
Modified 22 Mar 2012 for autoranking experiment
@author: lefterav
'''

import shutil
import os
import re
import sys

#pipeline essentials
from ruffus import *
#from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph, pipeline_printout

#internal code classes
from bootstrap import cfg
from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml 
from io_utils import saxjcml
from featuregenerator.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
from featuregenerator.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.bleu.bleugenerator import CrossBleuGenerator, BleuGenerator
from featuregenerator.meteor.meteor import CrossMeteorGenerator, MeteorGenerator
from featuregenerator.attribute_rank import AttributeRankGenerator
from io_utils.input.xmlreader import XmlReader
from featuregenerator.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.preprocessor import Normalizer
from featuregenerator.preprocessor import Tokenizer







gateway = cfg.java_init()

cores = int(cfg.get("general", "cores"))
parallel_feature_functions = []
sys.stderr.write("running with {} cores\n".format(cores)) 

path = cfg.get_path()
os.chdir(path)
source_language =  cfg.get("general", "source_language")
target_language =  cfg.get("general", "target_language")
training_sets = cfg.get("training", "filenames").split(",")
testing_set = cfg.get("testing", "filename")
all_sets = training_sets
#all_sets.append(testing_set)

print all_sets


def get_basename(filename):
    basename = re.findall("(.*)\.jcml", os.path.basename(filename))[0]
    print basename
    return basename

@split(None, "*orig.jcml", all_sets)
def data_fetch(input_file, output_files, external_files):
    """
    Fetch training file and place it comfortably in the working directory
    Files are expected to contain the set name, followed by the ending .jcml
    """
    for external_file in external_files:
        print "Moving here external file ", external_file
        basename = get_basename(external_file)
        print "Found basename" 
        basename = basename.replace(".", "-")
        
        output_file = "{0}.{1}".format(basename, "orig.jcml")
        print "output", output_file
        shutil.copy(external_file, output_file)

try:
    annotated_filenames = cfg.get("training", "annotated_filenames").split(",")
except:
    annotated_filenames = []



#@split(data_fetch,"*.ext.f.jcml", annotated_filenames)
#def add_externally_annotated_sets(input_file, output_files, external_files):
##    input_basename = get_basename(input_file)
#    for external_file in external_files:
#        external_basename = get_basename(external_file)
##        if input_basename == external_basename:
#        shutil.copy(external_file, "%s.ext.f.jcml" % external_basename)
#            
#if (cfg.exists_parser(target_language)):
#    parallel_feature_functions.append(add_externally_annotated_sets)

@transform(data_fetch, suffix("orig.jcml"), "tok.jcml")        
def preprocess_data(input_file, output_file):
    
    normalizer_src = Normalizer(source_language)
    normalizer_tgt = Normalizer(target_language)
    tokenizer_src = Tokenizer(source_language)
    tokenizer_tgt = Tokenizer(target_language)
    fgs = [normalizer_src, normalizer_tgt, tokenizer_src, tokenizer_tgt]
    
#    parallelsentences = JcmlReader(input_file).get_parallelsentences()
#    for fg in fgs:
#        parallelsentences = fg.add_features_batch(parallelsentences)
#    Parallelsentence2Jcml(parallelsentences).write_to_file(output_file)
    saxjcml.run_features_generator(input_file, output_file, fgs, True)
    
    


@jobs_limit(1, "checker")
@active_if(cfg.exists_checker(source_language))
@transform(data_fetch, suffix(".orig.jcml"), ".iq.%s.f.jcml" % source_language, source_language)
def features_checker_source(input_file, output_file, source_language):
#    features_checker(input_file, output_file, language_checker_source)
    cfg.get_checker(source_language).add_features_batch_xml(input_file, output_file)
#    saxjcml.run_features_generator(input_file, output_file, [cfg.get_checker(source_language)])
    #ATTENTION: for some reason, the checker has to be initialized via suds in the same thread as it is being run
if cfg.exists_checker(source_language):
    parallel_feature_functions.append(features_checker_source)


#language_checker_target = cfg.get_checker(target_language)


@jobs_limit(1, "checker")
@active_if(cfg.exists_checker(target_language))
@transform(data_fetch, suffix(".orig.jcml"), ".iq.%s.f.jcml" % target_language, target_language)
def features_checker_target(input_file, output_file, target_language):
#    features_checker(input_file, output_file, language_checker_target)
    cfg.get_checker(target_language).add_features_batch_xml(input_file, output_file)
#    saxjcml.run_features_generator(input_file, output_file, [cfg.get_checker(target_language)])
    
if cfg.exists_checker(target_language):
    parallel_feature_functions.append(features_checker_target)


#def features_checker(input_file, output_file, language_checker):
#    saxjcml.run_features_generator(input_file, output_file, [language_checker])


@jobs_limit(1, "ltool") #Dunno why, but only one language tool at a time
@active_if(cfg.has_section("languagetool"))
@transform(data_fetch, suffix(".orig.jcml"), ".lt.%s.f.jcml" % source_language, source_language)
def features_langtool_source(input_file, output_file, language):
    features_langtool(input_file, output_file, language)

@jobs_limit(1, "ltool")
@active_if(cfg.has_section("languagetool"))
@transform(data_fetch, suffix(".orig.jcml"), ".lt.%s.f.jcml" % target_language, target_language)
def features_langtool_target(input_file, output_file, language):
    features_langtool(input_file, output_file, language)
if cfg.has_section("languagetool"):
    parallel_feature_functions.append(features_langtool_target)
    parallel_feature_functions.append(features_langtool_source)

def features_langtool(input_file, output_file, language):
    fg = LanguageToolSocketFeatureGenerator(language, cfg.gateway)
    saxjcml.run_features_generator(input_file, output_file, [fg])



            
@split(preprocess_data, "*.part.jcml", cores)
def original_data_split(input_files, output_files, parts):
    """
    Split the datasets to parts, in order to perform heavy tasks
    """
    for input_file in input_files:
        print "splitting file", input_file
        re_split = "([^.]*)\.tok\.(jcml)"
        XmlReader(input_file).split_and_write(parts, re_split)

       
@active_if(cfg.exists_parser(source_language))
@transform(original_data_split, suffix("part.jcml"), "part.parsed.%s.f.jcml" % source_language, source_language, cfg.get_parser_name(source_language))
def features_berkeley_source(input_file, output_file, source_language, parser_name):
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

@active_if(cfg.exists_parser(source_language))
#@merge(features_berkeley_source, "parsed.%s.f.jcml" % source_language)
@collate(features_berkeley_source, regex(r"([^.]+)\.(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
def merge_parse_parts_source(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(source_language)):
    parallel_feature_functions.append(merge_parse_parts_source)

@active_if(cfg.exists_parser(target_language))
#@merge(features_berkeley_target, "parsed.%s.f.jcml" % target_language)
@collate(features_berkeley_target, regex(r"([^.]+)\.(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
def merge_parse_parts_target(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(target_language)):
    parallel_feature_functions.append(merge_parse_parts_target)


def merge_parts(inputs, output):
    parallelsentences = []
    for input in inputs:
        parallelsentences.extend(JcmlReader(input).get_parallelsentences())
    Parallelsentence2Jcml(parallelsentences).write_to_file(output)    



@transform(preprocess_data, suffix(".tok.jcml"), ".tc.%s.jcml" % source_language, source_language, cfg.get_truecaser_model(source_language))
def truecase_source(input_file, output_file, language, model):
    truecase(input_file, output_file, language, model)

@transform(preprocess_data, suffix(".tok.jcml"), ".tc.%s.jcml" % target_language, target_language, cfg.get_truecaser_model(target_language))
def truecase_target(input_file, output_file, language, model):
    truecase(input_file, output_file, language, model)

def truecase(input_file, output_file, language, model):
    from featuregenerator.preprocessor import Truecaser
    truecaser = Truecaser(language, model)
    saxjcml.run_features_generator(input_file, output_file, [truecaser])

@transform(truecase_target, suffix(".tc.%s.jcml" % target_language), ".bleu.%s.f.jcml" % target_language)
def cross_bleu(input_file, output_file):
    saxjcml.run_features_generator(input_file, output_file, [CrossBleuGenerator()])
parallel_feature_functions.append(cross_bleu)

@active_if(cfg.has_section("meteor"))
@transform(truecase_target, suffix(".tc.%s.jcml" % target_language), ".meteor.%s.f.jcml" % target_language, target_language, gateway)
def cross_meteor(input_file, output_file, target_language, gateway):
    saxjcml.run_features_generator(input_file, output_file, [CrossBleuGenerator(), CrossMeteorGenerator(target_language, gateway)])

if cfg.has_section("meteor"):    
    parallel_feature_functions.append(cross_meteor)
    
#    parallelsentences = JcmlReader(input_file).get_parallelsentences()
#    parallelsentences = truecaser.add_features_batch(parallelsentences)
#    Parallelsentence2Jcml(parallelsentences).write_to_file(output_file)
    

@active_if(cfg.exists_lm(source_language))
@transform(truecase_source, suffix(".tc.%s.jcml" % source_language), ".lm.%s.f.jcml" % source_language, source_language, cfg.get_lm_name(source_language)) 
def features_lm_source(input_file, output_file, language, lm_name):
    features_lm(input_file, output_file, language, lm_name)
    #saxjcml.run_features_generator(input_file, output_file, [srilm_ngram])
if (cfg.exists_lm(source_language)):
    parallel_feature_functions.append(features_lm_source)

@active_if(cfg.exists_lm(target_language))
@transform(truecase_target, suffix(".tc.%s.jcml" % target_language), ".lm.%s.f.jcml" % target_language, target_language, cfg.get_lm_name(target_language)) 
def features_lm_target(input_file, output_file, language, lm_name):
    features_lm(input_file, output_file, language, lm_name)
if (cfg.exists_lm(target_language)):
    parallel_feature_functions.append(features_lm_target)
    
def features_lm(input_file, output_file, language, lm_name):
    features_lm_batch(input_file, output_file, language, lm_name)

def features_lm_batch(input_file, output_file, language, lm_name):
    srilmgenerator = cfg.get_lm(language) 
    processed_parallelsentences = srilmgenerator.add_features_batch(JcmlReader(input_file).get_parallelsentences())
    Parallelsentence2Jcml(processed_parallelsentences).write_to_file(output_file)

#unimplemented
def features_lm_single(input_file, output_file, language, lm_url, lm_tokenize, lm_lowercase):
    pass


#language_checker_source = cfg.get_checker(source_language)





@active_if(False)
def features_ibm(input_file, output_file, ibm1lexicon):
    ibmfeaturegenerator = Ibm1FeatureGenerator(ibm1lexicon)
    saxjcml.run_features_generator(input_file, output_file, [ibmfeaturegenerator])
    


#active_parallel_feature_functions = [function for function in parallel_feature_functions if function.is_active]

#first part of the regular expression is the basename of the dataset
@collate(parallel_feature_functions, regex(r"([^.]+)\.(.+)\.f.jcml"),  r"\1.all.f.jcml")
def features_gather(singledataset_annotations, gathered_singledataset_annotations):
    
    print "gathering features from tasks ", parallel_feature_functions
    
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
                 #LevenshteinGenerator(),
                 RatioGenerator()]
    saxjcml.run_features_generator(input_file, output_file, analyzers)
    

@active_if(cfg.getboolean("annotation", "reference_features"))
@transform(data_fetch, suffix(".orig.jcml"), ".ref.f.jcml", cfg.get("annotation", "moreisbetter").split(","), cfg.get("annotation", "lessisbetter").split(",")) 
def reference_features(input_file, output_file, moreisbetter_atts, lessisbetter_atts):
    analyzers = [LevenshteinGenerator(),
                 BleuGenerator()]
    
    if cfg.has_section("meteor"):
        analyzers.append(MeteorGenerator()),
        
    analyzers.append(RatioGenerator())
    
    for attribute in moreisbetter_atts:
        analyzers.append(AttributeRankGenerator(attribute, None, True))
    for attribute in lessisbetter_atts:
        analyzers.append(AttributeRankGenerator(attribute))
        
    saxjcml.run_features_generator(input_file, output_file, analyzers)


def create_ranks():
    pass



if __name__ == '__main__':
    
    
    pipeline_printout_graph("flowchart.pdf", "pdf", [analyze_external_features])
    
    pipeline_run([analyze_external_features], multiprocess = cores, verbose = 5)
    #pipeline_run([original_data_split], multiprocess = 2)

print "Done!"
cfg.java_terminate()