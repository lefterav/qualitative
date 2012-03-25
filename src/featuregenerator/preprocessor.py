'''
Created on 24 Mar 2012

@author: lefterav
'''

from featuregenerator import FeatureGenerator
import subprocess
import util
import os

class Preprocessor(FeatureGenerator):
    """
    """
    def __init__(self, lang):
        self.lang = lang
    
    def add_features_src(self, simplesentence, parallelsentence = None):
        src_lang = parallelsentence.get_attribute("langsrc") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.lang:
            simplesentence.string = self.process_string(simplesentence.string)  
        return simplesentence
    
    def add_features_tgt(self, simplesentence, parallelsentence = None):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            simplesentence.string = self.process_string(simplesentence.string)  
        return simplesentence
    
    
    def process_string(self, string):
        raise NotImplementedError
    
    
class CommandlinePreprocessor(Preprocessor):
    def __init__(self, path, lang, params = {}, command_template = ""):
        self.lang = lang
        params["lang"] = lang
        params["path"] = path
        command = command_template.format(**params)
        command_items = command.split(' ')
        self.output = []
        self.running = True
        
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=0, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        )
    
    def process_string(self, string):
        print >>self.process.stdin, string
        self.process.stdin.flush()       
        output = self.process.stdout.readline()
        return output
    
    def close(self):
        self.running = False
        try:
            self.process.stdin.close()
            self.process.terminate()
        except:
            pass
    
    def __del__(self):
        self.close()

class Normalizer(CommandlinePreprocessor):
    def __init__(self, lang):
        path = util.__path__[0]
        path = os.path.join(path, "normalize-punctuation.perl")
        command_template = "perl {path} -b -l {lang}"
        super(Normalizer, self).__init__(path, lang, {}, command_template)
        
class Tokenizer(CommandlinePreprocessor):
    def __init__(self, lang):
        path = util.__path__[0]
        path = os.path.join(path, "tokenizer.perl")
        command_template = "perl {path} -b -l {lang}"
        super(Tokenizer, self).__init__(path, lang, {}, command_template)

class Truecaser(CommandlinePreprocessor):
    def __init__(self, lang, model):
        path = util.__path__[0]
        path = os.path.join(path, "truecase.perl")
        command_template = "perl {path} -model {model}"
        super(Truecaser, self).__init__(path, lang, {"model": model}, command_template)

    
    
if __name__ == '__main__':
    from io_utils.input.jcmlreader import JcmlReader
    from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
    #path = "/home/lefterav/taraxu_tools/scripts/tokenizer/tokenizer.perl"
    #command_template = "{path} -b -l {lang}"
#    path = "/home/lefterav/taraxu_tools/scripts/tokenizer/normalize-punctuation.perl"
#    command_template = "perl {path} -l {lang} -b"
    tokenizer = Tokenizer("en")
    parallelsentences = JcmlReader("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/training-sample.orig.jcml").get_parallelsentences()
    tokenized = tokenizer.add_features_batch(parallelsentences)
    #tokenizer.close()
    Parallelsentence2Jcml(tokenized).write_to_file("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/training-sample.tok.jcml")
    