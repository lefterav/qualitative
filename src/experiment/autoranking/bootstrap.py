"""bootstrap.py
    module to set up a pipeline program
"""


import StringIO
from ConfigParser import ConfigParser
import classifier
from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator, BerkeleyXMLRPCFeatureGenerator
from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator 
import pkgutil
import Orange
import os
import shutil
import re

#from experiment.utils.ruffus_utils import (touch, sys_call,
#                                           main_logger as log,
#                                           main_mutex as log_mtx)

# --- config and options---
CONFIG_FILENAME = os.path.join(os.path.dirname(__name__), 'config/pipeline.cfg')
print 'config', CONFIG_FILENAME 
CONFIG_TEMPLATE = """
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
        return getattr(Orange, name)
    
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
    
    
    def exists_checker(self, language):
        for checker_name in [section for section in self.sections() if section.startswith("checker:")]:
            if self.get(checker_name, "language") == language:
                return True
        return False
    
    
    def _get_checker_settings(self, checker_name):
        settings = {}
        for option in self.options(checker_name):
            if option.startswith("setting_"):
                setting_name = re.findall("setting_(.*)", option)[0]
                setting_value = self.get(checker_name, option)
                settings[setting_name] = setting_value
        return settings
    
    
    def get_checker(self, language):
        #@todo: see how to generalize this. also pass parameters read by the pipeline, currently hardcoded
        for checker_name in [section for section in self.sections() if section.startswith("checker:")]:
            print "looking on checker ", checker_name , language
            if self.get(checker_name, "language") == language:
                #TODO: if KenLM gets wrapped up, add a type: setting
                from featuregenerator.iq.acrolinxclient import IQFeatureGenerator
                
                settings = self._get_checker_settings(checker_name)
                
                feature_generator = IQFeatureGenerator(language,
                                                       settings,
                                                       self.get(checker_name, "user_id"),
                                                       self.get(checker_name, "host"),
                                                       self.get(checker_name, "wsdl_path"),
                                                       self.get(checker_name, "protocol"),
                                                       self.get(checker_name, "license_file")
                                                       )
                print "returning feature generator"
                return feature_generator
        print "Failure with checker for", language
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

    def get_truecaser_model(self, language):
        for tc_name in [section for section in self.sections() if section.startswith("tc:")]:
            if self.get(tc_name, "language") == language:        
                return self.get(tc_name, "model")
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

#try:
#    configfilename = os.sys.argv[1]
#except IndexError:
#    configfilename = CONFIG_FILENAME



    
# global configuration
cfg = ExperimentConfigParser()
cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE))  # set up defaults
#cfg.read(CONFIG_FILENAME)  # add user-specified settings
#cfg.read(configfilename)  # add user-specified settings

try: 
    cfg.read(CONFIG_FILENAME)
except:
    print "cannot read original cfg file"
    pass

try: 
    cfg.read(os.sys.argv[1])
except:
    print "cannot read additional cfg file"
    pass

try:
    continue_experiment = os.sys.argv[2]
except:
    continue_experiment = None

path = cfg.prepare_dir(continue_experiment)
#os.chdir(path)

