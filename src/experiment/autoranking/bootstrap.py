"""bootstrap.py
    module to set up a pipeline program
"""


import StringIO
from ConfigParser import ConfigParser
import classifier
from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator, BerkeleyFeatureGenerator, BerkeleyXMLRPCFeatureGenerator 
import pkgutil
import orange

#from experiment.utils.ruffus_utils import (touch, sys_call,
#                                           main_logger as log,
#                                           main_mutex as log_mtx)

# --- config and options---
CONFIG_FILENAME = 'pipeline.cfg'
CONFIG_TEMPLATE = """
[general]
path = /home/elav01/taraxu_data/selection-mechanism/ml4hmt/experiment/109
source_language = de
target_language = en


[annotation]
filenames = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt10-test.jcml
reference_features = False
moreisbetter = bleu
lessisbetter = lev

[parser:berkeley_en:soc]
type = socket
grammarfile = /home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr
berkeley_parser_jar = /home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar
py4j_jar = /usr/share/py4j/py4j0.7.jar
language = en
tokenize = False

#[parser:berkeley_en]
#type = xmlrpc
#language = en
#url = http://percival.sb.dfki.de:8682
#tokenize = False
#
#[parser:berkeley_es]
#type = xmlrpc
#language = es
#url = http://percival.sb.dfki.de:21115
#tokenize = False
#
#[parser:berkeley_de]
#type = xmlrpc
#language = de
#url = http://percival.sb.dfki.de:8684
#tokenize = False

[lmserver:lm_en]
language = en
lowercase = True
tokenize = True
url = http://percival.sb.dfki.de:8585

[lmserver:lm_de]
language = de
lowercase = True
tokenize = True
url = http://percival.sb.dfki.de:8585


[preprocessing]
pairwise = True
pairwise_exponential = True
allow_ties = False
generate_diff = False
merge_overlapping = True
orange_minimal = False

[training]
filenames = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt08.if.partial.jcml
#,/home/elav01/workspace/TaraXUscripts/data/multiclass/wmt10-train.partial.if.jcml
class_name = rank
meta_attributes=id,testset
attributes = tgt-1_unk,tgt-2_unk,tgt-1_tri-prob,tgt-2_tri-prob,tgt-1_length_ratio,tgt-2_length_ratio,tgt-1_berkeley-n_ratio,tgt-2_berkeley-n_ratio,tgt-1_berkeley-n,tgt-2_berkeley-n,tgt-1_parse-VB,tgt-2_parse-VB
continuize=True
multinomialTreatment=NValues
continuousTreatment=NormalizeBySpan
classTreatment=Ignore
classifier=Bayes

[testing]
filenames = /home/elav01/taraxu_data/wmt-annotated/wmt10.ex.3.sample.jcml,/home/elav01/workspace/TaraXUscripts/data/multiclass/wmt08.if.partial.jcml
"""



class ExperimentConfigParser(ConfigParser):
    
    def get_classifier(self, name = None):
        if not name:
            name = self.get("training", "classifier")
        package = classifier
        prefix = package.__name__ + '.'
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            module = __import__(modname, fromlist="dummy")
            try:
                return getattr(module, name)
            except:
                pass
        return getattr(orange, name)
    
    
    def exists_parser(self, language):
        for parser_name in [section for section in cfg.sections() if section.startswith("parser:")]:
            if cfg.get(parser_name, "language") == language:
                return True
        return False
    
    def get_parser(self, language):
        #this is reading the configuration, maybe move elsewher
        for parser_name in [section for section in cfg.sections() if section.startswith("parser:")]:
            if cfg.get(parser_name, "language") == language:
                tokenize = cfg.getboolean(parser_name, "tokenize")
                if cfg.get(parser_name, "type") == "xmlrpc":
                    url = cfg.get(parser_name, "url")
                    return BerkeleyXMLRPCFeatureGenerator(url, language, tokenize)
                elif cfg.get(parser_name, "type") == "socket":
                    print "initializing socket parser"
                    grammarfile = cfg.get(parser_name, "grammarfile")
                    berkeley_parser_jar = cfg.get(parser_name, "berkeley_parser_jar")
                    py4j_jar = cfg.get(parser_name, "py4j_jar")
                    return BerkeleySocketFeatureGenerator(grammarfile, berkeley_parser_jar, py4j_jar, language, tokenize)
        return False
    
    
    def get_parser_name(self, language):
        for parser_name in [section for section in cfg.sections() if section.startswith("parser:")]:
            if cfg.get(parser_name, "language") == language:
                return parser_name
        return None
    
# global configuration
cfg = ExperimentConfigParser()
cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE))  # set up defaults
cfg.read(CONFIG_FILENAME)  # add user-specified settings
#
#def genome_path():
#    'returns the path to the genome fasta file (and downloads it if necessary)'
#    genome = worldbase(cfg.get('DEFAULT', 'worldbase_genome'), download=True)
#    return genome.filepath
#
#
#@files(None, genome_path())
#def get_genome(_, out_genome_path, touch_file=True):
#    'download the worldbase genome'
#    genome = worldbase(cfg.get('DEFAULT', 'worldbase_genome'), download=True)
#    if touch_file:
#        touch(out_genome_path)
#    return genome
#
#
#@files(None, '%s.chrom.sizes' % genome_path())
#def get_chrom_sizes(_, out_sizes):
#    'retrieve the chromosome sizes for the current genome from UCSC'
#    cmd = 'fetchChromSizes %s > %s' % (cfg.get('DEFAULT', 'genome'), out_sizes)
#    sys_call(cmd, file_log=False)
