'''
Created on 24 Mar 2012

@author: lefterav
'''

from featuregenerator import FeatureGenerator
import subprocess
import util
import codecs
import os

import Queue
import threading
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
    
    
    def _enqueue_output(self, stdout, queue):
        out = 0
        for line in iter(stdout.readline, ''):
            print "thread received response: ", line
            queue.put(line)
#            break



    



    
    def __init__(self, path, lang, params = {}, command_template = ""):
        self.lang = lang
        params["lang"] = lang
        params["path"] = path
        self.command = command_template.format(**params)
        command_items = self.command.split(' ')
        self.output = []
        self.running = True
        
        print "starting process"
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=1, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        )
        

        
#        self.q = Queue.Queue()
#        t = threading.Thread(target = self._enqueue_output, args = (self.process.stdout, self.q))
#
#        t.daemon = True
#        t.start()
        
        
        
        print "process started"
        
        #self.process.stdin = codecs.getwriter('utf-8')(self.process.stdin)
        #self.process.stdout = codecs.getreader('utf-8')(self.process.stdout)
    
    def process_string(self, string):
        #string = string.decode('utf-8')
        
        #string = string.encode('utf-8')
        self.process.stdin.write('{0}{1}\n'.format(string, ' '*10240))
        print "sent sentence"
        
        
        self.process.stdin.flush()   
        self.process.stdout.flush()
        
        output = self.process.stdout.readline().strip()
        print output

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
                
        f, filename = tempfile.mkstemp(text=True)
        os.close(f)
        print filename
        f = open(filename, 'w')
        for string in strings:
            f.write(string)
            f.write('\n')
        f.close()
        return filename
    
    def _get_tool_output(self, strings):
        tmpfilename = self._get_temporary_file(strings)
        tmpfile = open(tmpfilename, 'r')
        commanditems = self.command.split(' ')
        output = subprocess.check_output(commanditems, stdin=tmpfile).split('\n')
        tmpfile.close()
        #os.remove(tmpfile)
        return output
            
#    def add_features_batch(self, parallelsentences):
#        dataset = DataSet(parallelsentences)
#        
#        if dataset.get_parallelsentences()[0].get_attribute("langsrc") == self.lang:
#            sourcestrings = dataset.get_singlesource_strings()
#            processed_sourcestrings = self._get_tool_output(sourcestrings)
#            dataset.modify_singlesource_strings(processed_sourcestrings)
#        
#        
#        if dataset.get_parallelsentences()[0].get_attribute("langtgt") == self.lang:
#            targetstringlists = dataset.get_target_strings()
#            processed_targetstringslist = [self._get_tool_output(targetstrings) for targetstrings in targetstringlists]
#            dataset.modify_target_strings(processed_targetstringslist)
#        
#        return dataset.get_parallelsentences()
#    

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
    parallelsentences = JcmlReader("/home/elav01/taraxu_data/jcml-latest/clean/wmt2011.newstest.en-de.rank-clean.jcml").get_parallelsentences()
    tokenized = tokenizer.add_features_batch(parallelsentences)
    #tokenizer.close()
    Parallelsentence2Jcml(tokenized).write_to_file("/home/elav01/taraxu_data/jcml-latest/tok/wmt2011.newstest.en-de.rank-clean.jcml")
    