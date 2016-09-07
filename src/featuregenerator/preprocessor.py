'''
Implementation of text preprocessors, including external commandline tools via pipes (tokenizer, truecaser, etc.) 

Created on 24 Mar 2012

@author: Eleftherios Avramidis
'''

from . import FeatureGenerator
import subprocess
import util
import os
import logging as log
from xml.sax import saxutils

class Preprocessor(FeatureGenerator):
    """
    Base class for a text pre-processor, to be inherited by applied pre-processors such as tokenizers etc.
    Contrary to the majority of feature generators, pre-processors do not return features/attributes, but
    instead they modify the string content of the sentences. For this purpose the order of pre-processors
    in an annotation pipeline is important.
    
    Implemented methods of the base class divert the content of source or target sentences to the 
    process_string function, which should do the job which is particular to the string. Strings are 
    processed only if they comply with the language of the pre-processor
    
    @ivar language: language code of supported language
    @type language: str
    """
    def __init__(self, language):
        """
        @param language: language code of supported language
        @type language: str
        """
        self.language = language
    
    def add_features_src(self, simplesentence, parallelsentence = None):
        src_lang = parallelsentence.get_attribute("langsrc") #TODO: make this format independent by adding it as an attribute of the sentence objects
        if src_lang == self.language:
            simplesentence.string = self.process_string(simplesentence.string)  
        return simplesentence
    
    def add_features_tgt(self, simplesentence, parallelsentence = None):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.language:
            simplesentence.string = self.process_string(simplesentence.get_string())  
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
    @ivar language: language code
    @type language: str
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
    
    def __init__(self, path, language, params = {}, command_template = "", unescape=False):
        """
        Initialize commandline-based feature generator. 
        @param path: the path where the command is based
        @type path: str
        @param language: the language code for the supported language
        @type language: str
        @param params: commandline parameters for internal process
        @type params: dict((str, str))
        @param command_template: the template of the command
        @type command_template: str        
        """
        self.language = language
        params["language"] = language
        params["path"] = path
        self.command = command_template.format(**params)
        log.debug("Command of preprocessor: '{}'".format(self.command))
        command_items = self.command.split(' ')
        self.output = []
        self.running = True
        self.unescape = unescape
        

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
        
        
        

        #block input        
        #self.process.stdin = codecs.getwriter('utf-8')(self.process.stdin)
        #self.process.stdout = codecs.getreader('utf-8')(self.process.stdout)
    
    def process_string(self, string):
        if isinstance(string, unicode):
            string = u'{0}{1}\n'.format(string, u' '*10240)
            string = string.encode('utf-8')
        else:
            string = '{0}{1}\n'.format(string, ' '*10240)
        self.process.stdin.write(string)
        self.process.stdin.flush()   
        self.process.stdout.flush()
        
        output = self.process.stdout.readline().strip()
        
        #some preprocessors occasionally return an empty string. In that case read once more
        if output == "" and len(string) > 1:
            output = self.process.stdout.readline().strip()
        
        if self.unescape:
            output = saxutils.unescape(output)
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
#        if dataset.get_parallelsentences()[0].get_attribute("langsrc") == self.language:
#            sourcestrings = dataset.get_singlesource_strings()
#            processed_sourcestrings = self._get_tool_output(sourcestrings)
#            dataset.modify_singlesource_strings(processed_sourcestrings)
#        
#        
#        if dataset.get_parallelsentences()[0].get_attribute("langtgt") == self.language:
#            targetstringlists = dataset.get_target_strings()
#            processed_targetstringslist = [self._get_tool_output(targetstrings) for targetstrings in targetstringlists]
#            dataset.modify_target_strings(processed_targetstringslist)
#        
#        return dataset.get_parallelsentences()
#    

class Normalizer(CommandlinePreprocessor):
    def __init__(self, language):
        path = util.__path__[0]
        path = os.path.join(path, "normalize-punctuation.perl")
        command_template = "perl {path} -b -l {language}"
        super(Normalizer, self).__init__(path, language, {}, command_template)
        
class Tokenizer(CommandlinePreprocessor):
    def __init__(self, language, protected=None, unescape=True):
        path = util.__path__[0]
        path = os.path.join(path, "tokenizer.perl")
        command_template = "perl {path} -b -l {language}"
        if protected:
            command_template = "perl {path} -b -l {language} -protected {protected}"
        super(Tokenizer, self).__init__(path, language, {'protected': protected}, 
                command_template, unescape=unescape)

class Detokenizer(CommandlinePreprocessor):
    def __init__(self, language):
        path = util.__path__[0]
        path = os.path.join(path, "detokenizer.perl")
        command_template = "perl {path} -b -l {language}"
        super(Detokenizer, self).__init__(path, language, {}, command_template)
    

class Truecaser(CommandlinePreprocessor):
    def __init__(self, language, filename):
        path = util.__path__[0]
        path = os.path.join(path, "truecase.perl")
        command_template = "perl {path} --model {filename}"
        super(Truecaser, self).__init__(path, language, {"filename": filename}, command_template)

class Detruecaser(CommandlinePreprocessor):
    def __init__(self, language):
        path = util.__path__[0]
        path = os.path.join(path, "detruecase.perl")
        command_template = "perl {path} -b"
        super(Detruecaser, self).__init__(path, language, {}, command_template)

class CompoundSplitter(CommandlinePreprocessor):
    def __init__(self, language, filename):
        path = util.__path__[0]
        path = os.path.join(path, 'compound-splitter.perl')
        command_template = "perl {path} --model {filename}"
        super(CompoundSplitter, self).__init__(path, language, {"filename": filename}, command_template)   



    
if __name__ == '__main__':
    from dataprocessor.input.jcmlreader import JcmlReader
    from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
    import sys
    #path = "/home/Eleftherios Avramidis/taraxu_tools/scripts/tokenizer/tokenizer.perl"
    #command_template = "{path} -b -l {language}"
#    path = "/home/Eleftherios Avramidis/taraxu_tools/scripts/tokenizer/normalize-punctuation.perl"
#    command_template = "perl {path} -l {language} -b"
    tokenizer = Tokenizer("en")
    parallelsentences = JcmlReader(sys.argv[1]).get_parallelsentences()
    tokenized = tokenizer.add_features_batch(parallelsentences)
    #tokenizer.close()
    Parallelsentence2Jcml(tokenized).write_to_file(sys.argv[1].replace(".jcml", ".tok.jcml"))
    
