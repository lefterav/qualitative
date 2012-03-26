'''
Created on 24 Mar 2012

@author: lefterav
'''

from featuregenerator import FeatureGenerator
import subprocess
import util
import codecs
import os
from sentence.dataset import DataSet

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
        self.command = command_template.format(**params)
        command_items = self.command.split(' ')
        self.output = []
        self.running = True
        
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=0, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        )
        
        
        #self.process.stdin = codecs.getwriter('utf-8')(self.process.stdin)
        #self.process.stdout = codecs.getreader('utf-8')(self.process.stdout)
    
    def process_string(self, string):
        #string = string.decode('utf-8')
        
        #string = string.encode('utf-8')
        self.process.stdin.write(string)
        self.process.stdin.write("\n")
        self.process.stdin.flush()   
        self.process.stdout.flush()
    
        output = self.process.stdout.readline()
        self.process.stdout.flush()
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
        
    
    def _get_temporary_file(self, strings):
        import tempfile
                
        file, filename = tempfile.mkstemp(text=True)
        file = open(filename, 'w')
        for string in strings:
            file.write(string)
            file.write('\n')
        file.close()
        return filename
    
    def _get_tool_output(self, strings):
        tmpfilename = self._get_temporary_file(strings)
        tmpfile = open(tmpfilename, 'r')
        commanditems = self.command.split(' ')
        output = subprocess.check_output(commanditems, stdin=tmpfile).split('\n')
        tmpfile.close()
        #os.remove(tmpfile)
        return output
            
    def add_features_batch(self, parallelsentences):
        dataset = DataSet(parallelsentences)
        
        if dataset.get_parallelsentences.get_attribute("langsrc") == self.lang:
            sourcestrings = dataset.get_singlesource_strings()
            processed_sourcestrings = self._get_tool_output(sourcestrings)
            dataset.modify_singlesource_strings(processed_sourcestrings)
        
        
        if dataset.get_parallelsentences.get_attribute("langtgt") == self.lang:
            targetstringlists = dataset.get_target_strings()
            for targetstrings in targetstringlists:
                processed_targetstrings = self._get_tool_output(targetstrings)
                dataset.modify_target_strings(processed_targetstrings)
        
        return dataset.get_parallelsentences()
    

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
    parallelsentences = JcmlReader("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/wmt00-test-devpart.orig.jcml").get_parallelsentences()
    tokenized = tokenizer.add_features_batch(parallelsentences)
    #tokenizer.close()
    Parallelsentence2Jcml(tokenized).write_to_file("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/training-sample.tok.jcml")
    