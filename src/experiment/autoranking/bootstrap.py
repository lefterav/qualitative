"""bootstrap.py
    module to set up a pipeline program
"""


import StringIO
from ConfigParser import ConfigParser
import classifier
from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator, BerkeleyXMLRPCFeatureGenerator
from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator 
import pkgutil
import orange
import os
import shutil

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
filenames = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt10-test-devpart.jcml
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

[lm:lm_en]
language = en
lowercase = True
tokenize = True
url = http://percival.sb.dfki.de:8586

[lm:lm_de]
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
filenames = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt08.test.jcml
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
filename = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt10-test-devpart.jcml
#,/home/elav01/workspace/TaraXUscripts/data/multiclass/wmt08.if.partial.jcml
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
            if self.get(parser_name, "language") == language:
                tokenize = self.getboolean(parser_name, "tokenize")
                if self.get(parser_name, "type") == "xmlrpc":
                    url = self.get(parser_name, "url")
                    return BerkeleyXMLRPCFeatureGenerator(url, language, tokenize)
                elif self.get(parser_name, "type") == "socket":
                    print "initializing socket parser"
                    grammarfile = self.get(parser_name, "grammarfile")
                    berkeley_parser_jar = self.get(parser_name, "berkeley_parser_jar")
                    py4j_jar = self.get(parser_name, "py4j_jar")
                    return BerkeleySocketFeatureGenerator(grammarfile, berkeley_parser_jar, py4j_jar, language, tokenize)
        return False
    
    
    def get_parser_name(self, language):
        for parser_name in [section for section in self.sections() if section.startswith("parser:")]:
            if self.get(parser_name, "language") == language:
                return parser_name
        return None
    
    
    def get_source_language(self):
        return self.get("general", "source_language")
    
    def get_target_language(self):
        return self.get("general", "target_language")
    
    
    
    def exists_lm(self, language):
        for lm_name in [section for section in self.sections() if section.startswith("lm:")]:
            if self.get(lm_name, "language") == language:
                return True
        return False
    
    def get_lm(self, language):
        #TODO: probably establish sth like ExternalProcessor object and wrap all these params there
        for lm_name in [section for section in self.sections() if section.startswith("lm:")]:
            if self.get(lm_name, "language") == language:
                #TODO: if KenLM gets wrapped up, add a type: setting
                lm_url = self.get(lm_name, "url")
                lm_tokenize = self.getboolean(lm_name, "tokenize")
                lm_lowercase = self.getboolean(lm_name, "lowercase")
                srilm_generator = SRILMngramGenerator(lm_url, language, lm_lowercase, lm_tokenize)
                return srilm_generator
        return None
    
    
    def get_lm_name(self, language):
        for lm_name in [section for section in self.sections() if section.startswith("lm:")]:
            if self.get(lm_name, "language") == language:        
                return lm_name
        return ""

    def get_path(self):
        return self.path

    def prepare_dir(self, continue_step = None):
        
        path = self.get("general", "path")
        
        #first check whether the path of the "pool" exists or create it
        try:
            existing_files = os.listdir(path)
        except:
            os.makedirs(path)
            existing_files = []
        
        if continue_step:
            current_step_id = continue_step
            path = os.path.join(path, str(current_step_id))
        else:
            current_step_id = self._get_new_step_id(existing_files)
            path = os.path.join(path, str(current_step_id))
            os.mkdir(path)
               
        os.chdir(path)
        #copy all configuration settings to the new directory
        new_configfile = open("experiment.cfg",'w')
        self.write(new_configfile)
        new_configfile.close()
        self.path = path
        return path
    
    def _get_new_step_id(self, existing_files):
        #subdirectories should only have as name the integer id of the experiment
        filename_ids = []
        for filename in existing_files: #@todo add check if is directory or do better listing
            try:
                filename_ids.append(int(filename))
            except:
                pass
        current_step_id = 1
        
        #add one to the get the id of this experiment
        if filename_ids:
            highestnum = max(filename_ids)
            current_step_id = highestnum + 1
        return current_step_id 

try:
    configfilename = os.sys.argv[1]
except IndexError:
    configfilename = CONFIG_FILENAME
    
# global configuration
cfg = ExperimentConfigParser()
cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE))  # set up defaults
#cfg.read(CONFIG_FILENAME)  # add user-specified settings
cfg.read(CONFIG_FILENAME)  # add user-specified settings

path = cfg.prepare_dir()
#os.chdir(path)

