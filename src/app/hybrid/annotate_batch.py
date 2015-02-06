'''
Created on 17 Jan 2012
Modified 22 Mar 2012 for autoranking app
@author: Eleftherios Avramidis
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
from app.autoranking import bootstrap 
from featuregenerator.blackbox.parser.bitpar import BitParserFeatureGenerator,\
    BitParserBatchProcessor
cfg = bootstrap.get_cfg()
from dataprocessor.input.jcmlreader import JcmlReader
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml 
from dataprocessor.sax import saxjcml
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgRulesExtractor, CfgAlignmentFeatureGenerator
from featuregenerator.blackbox.counts import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.blackbox.ibm1 import AlignmentFeatureGenerator
from featuregenerator.reference.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.reference.bleu.bleugenerator import CrossBleuGenerator, BleuGenerator
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator, MeteorGenerator
from featuregenerator.reference.rgbf import RgbfGenerator
from featuregenerator.reference.wer.werfeaturegenerator import WERFeatureGenerator
from featuregenerator.reference.hjerson import Hjerson
from featuregenerator.attribute_rank import AttributeRankGenerator
from dataprocessor.input.xmlreader import XmlReader
from featuregenerator.blackbox.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
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

params = []
for external_file in all_sets:
    basename = get_basename(external_file)
    print "Found basename" 
    basename = basename.replace(".", "-")
    output_file = "{0}.{1}".format(basename, "orig.jcml")
    params.append([external_file, output_file])
    

@files(params)
def data_fetch(external_file, output_file):
    """
    Fetch training file and place it comfortably in the working directory
    Files are expected to contain the set name, followed by the ending .jcml
    """
#    for external_file in external_files:
    print "Moving here external file ", external_file
#    basename = get_basename(external_file)
#    print "Found basename" 
#    basename = basename.replace(".", "-")
    
#    output_file = "{0}.{1}".format(basename, "orig.jcml")
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
@transform(data_fetch, suffix(".orig.jcml"), ".lt.f.jcml" , source_language, target_language)
def features_langtool(input_file, output_file, source_language, target_language):
    fg_source = LanguageToolSocketFeatureGenerator(source_language, cfg.gateway)
    fg_target = LanguageToolSocketFeatureGenerator(target_language, cfg.gateway)
    saxjcml.run_features_generator(input_file, output_file, [fg_source, fg_target])


if cfg.has_section("languagetool"):
    parallel_feature_functions.append(features_langtool)


'''
Parallelized Berkley parser
'''
            
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

parse_functions = []

@active_if(cfg.exists_parser(source_language))
#@merge(features_berkeley_source, "parsed.%s.f.jcml" % source_language)
@collate(features_berkeley_source, regex(r"([^.]+)\.\s?(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
def merge_parse_parts_source(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(source_language)):
    parse_functions.append(merge_parse_parts_source)

@active_if(cfg.exists_parser(target_language))
#@merge(features_berkeley_target, "parsed.%s.f.jcml" % target_language)
@collate(features_berkeley_target, regex(r"([^.]+)\.\s?(\d+)\.part.parsed.([^.]+).f.jcml"),  r"\1.parsed.\3.f.jcml")
def merge_parse_parts_target(inputs, output):
    merge_parts(inputs, output)
if (cfg.exists_parser(target_language)):
    parse_functions.append(merge_parse_parts_target)


def merge_parts(inputs, output):
    print inputs
    parallelsentences = []
    for inp in sorted(inputs):
        parallelsentences.extend(JcmlReader(inp).get_parallelsentences())
    Parallelsentence2Jcml(parallelsentences).write_to_file(output)    


#first part of the regular expression is the basename of the dataset
@collate(parse_functions, regex(r"(.*)\.parsed.([^.]+).f.jcml"),  r"\1.parsed.f.jcml")
def merge_parse_source_target(tobermerged, gathered_singledataset_annotations):
    
    print "gathering berkeley parsing source and target ", parallel_feature_functions
    original_dataset = JcmlReader(tobermerged[0]).get_dataset()
    appended_dataset = JcmlReader(tobermerged[1]).get_dataset()
    original_dataset.merge_dataset_symmetrical(appended_dataset, {}, "id")
    Parallelsentence2Jcml(original_dataset.get_parallelsentences()).write_to_file(gathered_singledataset_annotations)

'''
IBM1 features over Berkeley parser output
'''

@transform(merge_parse_source_target, suffix(".parsed.f.jcml"), ".tc.parsed.f.jcml", cfg.get_truecaser_model(source_language), cfg.get_truecaser_model(target_language))
def truecase_parse_output(input_file, output_file, source_model, target_model):
    from featuregenerator.preprocessor import Truecaser
    
    truecaser_src = Truecaser(source_language, source_model)
    truecaser_tgt = Truecaser(target_language, target_model )
    
    fgs = [truecaser_src, truecaser_tgt]
    saxjcml.run_features_generator(input_file, output_file, fgs, True)
    
@transform(truecase_parse_output, suffix(".tc.parsed.f.jcml"), ".ibm1.f.jcml", cfg.get("ibm1", "source_lexicon"), cfg.get("ibm1", "target_lexicon"))    
def features_ibm1(input_file, output_file, sourcelexicon, targetlexicon):
    analyzers = [
             AlignmentFeatureGenerator(sourcelexicon, targetlexicon),
             CfgAlignmentFeatureGenerator(),
             ]
    saxjcml.run_features_generator(input_file, output_file, analyzers)
parallel_feature_functions.append(features_ibm1)


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
    
#Probably not used
@transform(preprocess_data, suffix(".tok.jcml"), ".tc.jcml", cfg.get_truecaser_model(source_language), cfg.get_truecaser_model(target_language))
def truecase_both(input_file, output_file, source_model, target_model):
    from featuregenerator.preprocessor import Truecaser
    
    truecaser_src = Truecaser(source_language, source_model)
    truecaser_tgt = Truecaser(target_language, target_model )
    
    fgs = [truecaser_src, truecaser_tgt]
    saxjcml.run_features_generator(input_file, output_file, fgs, True)


'''
Parallelized BitPar parsing
'''
bitpar_functions = []

bitpar_section = "parser:bitpar:{}".format(source_language)
@active_if(cfg.has_section("parser:bitpar:{}".format(source_language)))
@transform(original_data_split, suffix("part.jcml"), "part.bit.%s.f.jcml" % source_language, source_language, cfg.get(bitpar_section,"path"),  
        cfg.get(bitpar_section,"lexicon"),
        cfg.get(bitpar_section,"grammar"),
        cfg.get(bitpar_section,"unknownwords"),
        cfg.get(bitpar_section,"openclassdfsa"),
        path
        )

def features_bitpar_source(input_file, output_file, language, path, lexicon, grammar, unk, openclass, tmpdir):
    bitpar_section = "parser:bitpar:{}".format(language)
    bitpar = BitParserBatchProcessor(path,
                                     lexicon,
                                     grammar,
                                     unk,
                                     openclass,
                                     tmpdir=tmpdir
                                     )
    bitpar.process_source_batch(input_file, output_file)
    
bitpar_section = "parser:bitpar:{}".format(target_language)
@active_if(cfg.has_section("parser:bitpar:{}".format(target_language)))
@transform(original_data_split, suffix("part.jcml"), "part.bit.%s.f.jcml" % target_language, target_language, 
        cfg.get(bitpar_section,"path"),
        cfg.get(bitpar_section,"lexicon"),
        cfg.get(bitpar_section,"grammar"),
        cfg.get(bitpar_section,"unknownwords"),
        cfg.get(bitpar_section,"openclassdfsa"),
        path
        )

def features_bitpar_target(input_file, output_file, language, path, lexicon, grammar, unk, openclass, tmpdir):
    bitpar_section = "parser:bitpar:{}".format(language)
    bitpar = BitParserBatchProcessor(path,
                                     lexicon,
                                     grammar,
                                     unk,
                                     openclass,
                                     tmpdir=tmpdir
                                     )
    bitpar.process_target_batch(input_file, output_file)
    
@collate(features_bitpar_source, regex(r"([^.]+)\.\s?(\d+)\.part.bit.([^.]+).f.jcml"),  r"\1.bit.\3.f.jcml")
def merge_bitpar_parts_source(inputs, output):
    merge_parts(inputs, output)
if cfg.has_section("parser:bitpar:{}".format(source_language)):
    bitpar_functions.append(merge_bitpar_parts_source)

@collate(features_bitpar_target, regex(r"([^.]+)\.\s?(\d+)\.part.bit.([^.]+).f.jcml"),  r"\1.bit.\3.f.jcml")
def merge_bitpar_parts_target(inputs, output):
    merge_parts(inputs, output)
if cfg.has_section("parser:bitpar:{}".format(target_language)):
    bitpar_functions.append(merge_bitpar_parts_target)

@collate(bitpar_functions, regex(r"(.*)\.bit.([^.]+).f.jcml"),  r"\1.bit.f.jcml")
def merge_bitpar_source_target(tobermerged, gathered_singledataset_annotations):
    original_dataset = JcmlReader(tobermerged[0]).get_dataset()
    appended_dataset = JcmlReader(tobermerged[1]).get_dataset()
    original_dataset.merge_dataset_symmetrical(appended_dataset, {}, "id")
    Parallelsentence2Jcml(original_dataset.get_parallelsentences()).write_to_file(gathered_singledataset_annotations)

parallel_feature_functions.append(merge_bitpar_source_target)

'''
Cross BLEU and other features
'''

@transform(truecase_target, suffix(".tc.%s.jcml" % target_language), ".bleu.%s.f.jcml" % target_language)
def cross_bleu(input_file, output_file):
    saxjcml.run_features_generator(input_file, output_file, [CrossBleuGenerator()])
parallel_feature_functions.append(cross_bleu)


@active_if(cfg.has_section("meteor"))
@transform(truecase_target, suffix(".tc.%s.jcml" % target_language), ".meteor.%s.f.jcml" % target_language, target_language, cfg.get_classpath()[0], cfg.get_classpath()[1])
def cross_meteor(input_file, output_file, target_language, classpath, dir_path):
    saxjcml.run_features_generator(input_file, output_file, [CrossMeteorGenerator(target_language, gateway)])

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

@transform(preprocess_data, suffix(".tok.jcml"), ".l.f.jcml")
def features_length(input_file, output_file):
    saxjcml.run_features_generator(input_file, output_file, [LengthFeatureGenerator()])
parallel_feature_functions.append(features_length)
     

#@active_if(False)
#def features_ibm(input_file, output_file, ibm1lexicon):
#    ibmfeaturegenerator = AlignmentFeatureGenerator(ibm1lexicon)
#    saxjcml.run_features_generator(input_file, output_file, [ibmfeaturegenerator])

"""
Quest
"""
@transform(truecase_source, suffix(".tc.%s.jcml" % source_language), ".tc.%s-%s.jcml" % (source_language, target_language), target_language, cfg.get_truecaser_model(target_language))
def truecase_target_append(input_file, output_file, language, model):
    truecase(input_file, output_file, language, model)

@active_if(cfg.has_section('quest'))
@transform(truecase_target_append, suffix(".tc.%s-%s.jcml" % (source_language, target_language)), ".quest.f.jcml", source_language, target_language, cfg.get('quest', 'commandline'))
def features_quest(input_file, output_file, source_language, target_language, commandline):
    import subprocess, os, shutil
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)
    output_file_tmp = "{}.tmp".format(output_file)
    previous_path = os.path.abspath(os.curdir)
    os.chdir(cfg.get('quest', 'path'))
    subprocess.check_call(commandline.format(sourcelang=source_language, targetlang=target_language, inputfile=input_file, outputfile=output_file_tmp).split())
    os.chdir(previous_path)    
    shutil.move(output_file_tmp, output_file)

if cfg.has_section('quest'):
    parallel_feature_functions.append(features_quest)



@active_if(cfg.getboolean("annotation", "reference_features"))
@transform(truecase_target_append, suffix(".tc.%s-%s.jcml" % (source_language, target_language)), ".ref.f.jcml", cfg.get("annotation", "moreisbetter").split(","), cfg.get("annotation", "lessisbetter").split(","), cfg.get_classpath()[0], cfg.get_classpath()[1]) 
def reference_features(input_file, output_file, moreisbetter_atts, lessisbetter_atts, classpath, dir_path):
    analyzers = [LevenshteinGenerator(),
                 BleuGenerator(),
                 RgbfGenerator(),
                 WERFeatureGenerator(),
                 Hjerson()]
    if cfg.has_section("meteor"):
        analyzers.append(MeteorGenerator(target_language, gateway))
    saxjcml.run_features_generator(input_file, output_file, analyzers)
    
        
if cfg.getboolean("annotation", "reference_features"):
    parallel_feature_functions.append(reference_features)

#    analyzers.append(RatioGenerator())
    
#    for attribute in moreisbetter_atts:
#        analyzers.append(AttributeRankGenerator(attribute, None, True))
#    for attribute in lessisbetter_atts:
#        analyzers.append(AttributeRankGenerator(attribute))
#        

#active_parallel_feature_functions = [function for function in parallel_feature_functions if function.is_active]


    

#first part of the regular expression is the basename of the dataset
@collate(parallel_feature_functions, regex(r"([^.]+)\.(.+)\.f.jcml"),  r"\1.all.f.jcml")
def features_gather(singledataset_annotations, gathered_singledataset_annotations):
    
    
    tobermerged = singledataset_annotations
    print "gathering features from tasks ", parallel_feature_functions, tobermerged
    original_file = tobermerged[0]
    original_dataset = JcmlReader(original_file).get_dataset()
    for appended_file in tobermerged[1:]:
        appended_dataset = JcmlReader(appended_file).get_dataset()
        original_dataset.merge_dataset_symmetrical(appended_dataset, {}, "id")
    Parallelsentence2Jcml(original_dataset.get_parallelsentences()).write_to_file(gathered_singledataset_annotations)


    
@transform(features_gather, suffix(".all.f.jcml"), ".all.analyzed.f.jcml", cfg.get("general", "source_language"), cfg.get("general", "target_language"))    
def analyze_external_features(input_file, output_file, source_language, target_language):
    langpair = (source_language, target_language)

    analyzers = [
                 ParserMatches(langpair),
                 CfgRulesExtractor(),
                 RatioGenerator(),
                 ]
    saxjcml.run_features_generator(input_file, output_file, analyzers)
    




def create_ranks():
    pass



if __name__ == '__main__':
    
    
    pipeline_printout_graph("flowchart.pdf", "pdf", [analyze_external_features])
    
    pipeline_run([analyze_external_features], multiprocess = cores, verbose = 5)
    #pipeline_run([original_data_split], multiprocess = 2)

print "Done!"
cfg.java_terminate()
