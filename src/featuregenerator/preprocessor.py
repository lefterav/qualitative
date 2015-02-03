'''
Implementation of text preprocessors, including external commandline tools via pipes (tokenizer, truecaser, etc.) 

Created on 24 Mar 2012

@author: Eleftherios Avramidis
'''

from featuregenerator import FeatureGenerator
import subprocess
import util
import os
import time
import logging as log
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read

class Preprocessor(FeatureGenerator):
    """
    Base class for a text pre-processor, to be inherited by applied pre-processors such as tokenizers etc.
    Contrary to the majority of feature generators, pre-processors do not return features/attributes, but
    instead they modify the string content of the sentences. For this purpose the order of pre-processors
    in an annotation pipeline is important.
    
    Implemented methods of the base class divert the content of source or target sentences to the 
    process_string function, which should do the job which is particular to the string. Strings are 
    processed only if they comply with the language of the pre-processor
    
    @ivar lang: language code of supported language
    @type lang: str
    """
    def __init__(self, lang):
        """
        @param lang: language code of supported language
        @type lang: str
        """
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
        """
        Abstract class to be overriden by implemented pre-processors
        @param string: The string that needs to be pre-processed
        @type string: str
        @return: the string modified after pre-processing
        @rtype: str
        """
        raise NotImplementedError
    
    
class CommandlinePreprocessor(Preprocessor):
    """
    Base class for pre-processor wrapping a commandline process
    @ivar lang: language code
    @type lang: str
    @ivar running: boolean variable that signifies whether internal process is running or not
    @type running: boolena
    @ivar process: the encapsulated subprocess
    @type process: subprocess.Popen
    """    
    def _enqueue_output(self, stdout, queue):
        out = 0
        for line in iter(stdout.readline, ''):
            print "thread received response: ", line
            queue.put(line)
#            break
    
    def __init__(self, path, lang, params = {}, command_template = ""):
        """
        Initialize commandline-based feature generator. 
        @param path: the path where the command is based
        @type path: str
        @param lang: the language code for the supported language
        @type lang: str
        @param params: commandline parameters for internal process
        @type params: dict((str, str))
        @param command_template: the template of the command
        @type command_template: str        
        """
        self.lang = lang
        params["lang"] = lang
        params["path"] = path
        self.command = command_template.format(**params)
        command_items = self.command.split(' ')
        self.output = []
        self.running = True
        
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=1, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        )
        # set the O_NONBLOCK flag of p.stdout file descriptor:
        flags = fcntl(self.process.stdout, F_GETFL) # get current p.stdout flags
        fcntl(self.process.stdout, F_SETFL, flags | O_NONBLOCK)

#        self.q = Queue.Queue()
#        t = threading.Thread(target = self._enqueue_output, args = (self.process.stdout, self.q))
#
#        t.daemon = True
#        t.start()
        
        
        

        
        #self.process.stdin = codecs.getwriter('utf-8')(self.process.stdin)
        #self.process.stdout = codecs.getreader('utf-8')(self.process.stdout)
    
    def process_string(self, string):
        #string = string.decode('utf-8')
        
        #string = string.encode('utf-8')
#        self.process.stdin.write('{0}{1}\n'.format(string, ' '*10240))
        self.process.stdin.write(string)
        #self.process.stdin.flush()   
        #self.process.stdout.flush()
        time.sleep(0.1)
        #output = self.process.stdout.readline().strip()
        
        #some preprocessors occasionally return an empty string. In that case read once more
        #if output == "" and len(string) > 1:
        #    output = self.process.stdout.readline().strip()
        output = []
        while True:
           try:
               output.append(read(self.process.stdout.fileno(), 1024))
               log.debug("read one line")
           except OSError:
               # the os throws an exception if there is no data
               log.debug('[No more data]')
               break
        output = "".join(output)
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

class Detokenizer(CommandlinePreprocessor):
    def __init__(self, lang):
        path = util.__path__[0]
        path = os.path.join(path, "detokenizer.perl")
        command_template = "perl {path} -l {lang}"
        super(Detokenizer, self).__init__(path, lang, {}, command_template)
    

class Truecaser(CommandlinePreprocessor):
    def __init__(self, lang, model):
        path = util.__path__[0]
        path = os.path.join(path, "truecase.perl")
        command_template = "perl {path} -model {model}"
        super(Truecaser, self).__init__(path, lang, {"model": model}, command_template)

    
    
if __name__ == '__main__':
    from dataprocessor.input.jcmlreader import JcmlReader
    from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
    import sys
    #path = "/home/Eleftherios Avramidis/taraxu_tools/scripts/tokenizer/tokenizer.perl"
    #command_template = "{path} -b -l {lang}"
#    path = "/home/Eleftherios Avramidis/taraxu_tools/scripts/tokenizer/normalize-punctuation.perl"
#    command_template = "perl {path} -l {lang} -b"
    tokenizer = Tokenizer("en")
    parallelsentences = JcmlReader(sys.argv[1]).get_parallelsentences()
    tokenized = tokenizer.add_features_batch(parallelsentences)
    #tokenizer.close()
    Parallelsentence2Jcml(tokenized).write_to_file(sys.argv[1].replace(".jcml", ".tok.jcml"))
    
