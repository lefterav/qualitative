"""bootstrap.py
    module to set up a pipeline program
"""


import StringIO
from ConfigParser import ConfigParser, NoOptionError
from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator, BerkeleyXMLRPCFeatureGenerator
from featuregenerator.iq.acrolinxclient import IQFeatureGenerator
from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator 
import os
import re
import sys
import time
import random
import argparse
import fnmatch
import socket
from util.jvm import JVM
from py4j.java_gateway import GatewayClient, JavaGateway

# --- config and options---
CONFIG_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__name__), 'config/pipeline.cfg'))
print 'config', CONFIG_FILENAME 
CONFIG_TEMPLATE = """
"""


class ExperimentConfigParser(ConfigParser):
    """
    """
    checker = 0
    

    
    def java_init(self):
        
        #collect java classpath entries from all sections        
        java_classpath, dir_path = self.get_classpath()
        
        if java_classpath:
            
            self.jvm = JVM(java_classpath)
            socket_no = self.jvm.socket_no
            #socket_no = 25336
            self.gatewayclient = GatewayClient('localhost', socket_no)
            self.gateway = JavaGateway(self.gatewayclient, auto_convert=True, auto_field=True)
            sys.stderr.write("Initialized global Java gateway with pid {} in socket {}\n".format(self.jvm.pid, socket_no))
            return self.gateway
            # wait so that server starts
#            time.sleep(2)

    def get_classpath(self):
        java_classpath = set()
        for section in self.sections():
            try:
                java_classpath.add(self.get(section,"java_classpath"))
            except NoOptionError:
                pass
        if len(java_classpath) > 0:
            path = os.path.abspath(__file__)
            dir_path = os.path.dirname(path) #@todo: change location of the JavaServer to sth more universal
            java_classpath.add(dir_path)
            return list(java_classpath), dir_path
        return [], None

    def get_gatewayclient(self):
        try:
            return self.socket
        except:
            None
        
    
    def java_terminate(self):
        try:
            self.jvm.terminate()
        except:
            pass
        
    
    def getlearner(self):
        classifier_name = self.get("training",  "classifier") + "Learner"
        return eval(classifier_name)
    
    def get_classifier_params(self):
        self.classifier_params = eval(self.get("training", "params_%s" % self.get("training", "classifier")))
    
#    def get_classifier(self, name = None):
#        if not name:
#            name = self.get("training", "classifier")
#        package = classifier
#        prefix = package.__name__ + '.'
#        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
#            module = __import__(modname, fromlist="dummy")
#            try:
#                return getattr(module, name)
#            except:
#                pass
#        return getattr(Orange, name)
    
    def exists_parser(self, language):
        for parser_name in [section for section in self.sections() if section.startswith("parser:")]:
            if self.get(parser_name, "language") == language:
                return True
        return False
    
    def get_parser(self, language):
        #this is reading the configuration, maybe move elsewher
        for parser_name in [section for section in self.sections() if section.startswith("parser:")]:
            if self.get(parser_name, "language") == language:
                tokenize = self.getboolean(parser_name, "tokenize")
                if self.get(parser_name, "type") == "xmlrpc":
                    url = self.get(parser_name, "url")
                    return BerkeleyXMLRPCFeatureGenerator(url, language, tokenize)
                elif self.get(parser_name, "type") == "socket":
                    grammarfile = self.get(parser_name, "grammarfile")
                    sys.stderr.write("initializing socket parser with grammar file {}\n".format(grammarfile))
                    
#                    return BerkeleySocketFeatureGenerator(language, grammarfile, self.get_classpath())
                    return BerkeleySocketFeatureGenerator(language, grammarfile, self.gateway)
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
                wtime = random.randint(1, 15)
                time.sleep(wtime)
                #TODO: if KenLM gets wrapped up, add a type: setting
                
                settings = self._get_checker_settings(checker_name)
                                
                #user_id = "{}{}".format(self.get(checker_name, "user_id"), ExperimentConfigParser.checker)
#                user_id = self.get(checker_name, "user_id")
                #user_id = os.path.basename(tempfile.mktemp())
                user_id = socket.gethostname()
                
                feature_generator = IQFeatureGenerator(language,
                                                       settings,
                                                       user_id,
                                                       self.get(checker_name, "host"),
                                                       self.get(checker_name, "wsdl_path"),
                                                       self.get(checker_name, "protocol"),
                                                       "%s.dat" % user_id 
                                                       )
                print "returning feature generator with user_id", user_id
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
        new_configfile = open("app.cfg",'w')
        self.write(new_configfile)
        new_configfile.close()
        self.path = path
        sys.stderr.write("Working in path {}\n".format(path))
        sys.stderr.write("System process pid: {}\n".format(os.getpid()))
        return path
    
    def _get_new_step_id(self, existing_files):
        #subdirectories should only have as name the integer id of the app
        filename_ids = []
        for filename in existing_files: #@todo add check if is directory or do better listing
            try:
                filename_ids.append(int(filename))
            except:
                pass
        current_step_id = 1
        
        #add one to the get the id of this app
        if filename_ids:
            highestnum = max(filename_ids)
            current_step_id = highestnum + 1
        sys.stderr.write("Running app as step {0}\n".format(current_step_id))
        return current_step_id 
    
    def __del__(self):
        self.java_terminate()
        

#try:
#    configfilename = os.sys.argv[1]
#except IndexError:
#    configfilename = CONFIG_FILENAME

def get_cfg_files(config_filenames):
    cfg = ExperimentConfigParser()
    for config_filename in config_filenames:
        cfg.read(config_filename)
    return cfg

def get_cfg():

    # global configuration
    cfg = ExperimentConfigParser()
    cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE))  # set up defaults
    #cfg.read(CONFIG_FILENAME)  # add user-specified settings
    #cfg.read(configfilename)  # add user-specified settings
    
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', nargs='*', default=['cfg/pipeline.cfg'], help="Configuration files")
    parser.add_argument('--sourcelang', '-s', help="Source language code")
    parser.add_argument('--targetlang', '-t', help="Target language code")
    parser.add_argument('--selectpath', help="""If source and target language are set, 
                                                then use all files in the indicated directory 
                                                that have these language codes in their filename""")
    parser.add_argument('--cont', help="""If you want to resume an existing app, 
                                          specify its folder name heres. This must be 
                                          an existing dir name""")
    parser.add_argument('--cores',  help='How many cores should be parallelized')
    
    args = parser.parse_args()
    
    for config_filename in args.config:
        cfg.read(config_filename)
    
    continue_experiment = args.cont
    if args.sourcelang and args.targetlang and args.selectpath:
        #source-target lang code separated with hyphen
        filepattern = "*{}-{}*".format(args.sourcelang, args.targetlang) 
        available_files = os.listdir(args.selectpath)
        print available_files
        chosen_files = fnmatch.filter(available_files, filepattern)
        print chosen_files
        #prepend path
        chosen_files = [os.path.join(args.selectpath, f) for f in chosen_files] 
        cfg.set("general", "source_language", args.sourcelang)
        cfg.set("general", "target_language", args.targetlang)
        cfg.set("training", "filenames", ",".join(chosen_files))
    
    if args.cores:
        cfg.set("general", "cores", args.cores)
    
    path = cfg.prepare_dir(continue_experiment)
    
    #os.chdir(path)
    return cfg
    
