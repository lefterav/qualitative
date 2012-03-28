'''
Created on 24 Mar 2012

@author: lefterav
'''

import subprocess
import sys
import re
import codecs
import time
from threading  import Thread

from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

class LanguageToolFeatureGenerator(LanguageFeatureGenerator):
    '''
    classdocs
    '''
    
    def print_output(self, out):
        while self.running:
            self.output.append(out.readline())

    def __init__(self, path, lang, params = {}, command_template= 'java -jar {path} -v -l {lang} -b --api',):
        '''
        Constructor
        '''
        self.lang = lang
        params["lang"] = lang
        params["path"] = path
        command = command_template.format(**params)
        self.command = command
        command_items = command.split(' ')
        self.output = []
        self.running = True
        
        self.process = subprocess.Popen(command_items, 
                                        shell=False, 
                                        bufsize=0, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE
                                        )
#        self.process.stdout.readline()
#        self.process.stdout.readline()
        self.process.stdin = codecs.getwriter('utf-8')(self.process.stdin)
        self.process.stdout = codecs.getreader('utf-8')(self.process.stdout)
        #Thread(target=self.print_output, args=(self.process.stderr,)).start()
        Thread(target=self.print_output, args=(self.process.stdout,)).start()
        self.i = 0

    
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
        output = subprocess.check_output(commanditems, stdin=tmpfile, stderr=subprocess.STDOUT)
        tmpfile.close()
        #os.remove(tmpfile)
        return output
            
    def get_features_string(self, string):
        return self.postprocess_output(self._get_tool_output([string]))
        
    def get_features_string_pipe(self, string):
        print >>self.process.stdin, string + "\n"
        #print string
        self.process.stdin.flush()           
        self.i += 1
        output=[]
        
        self.process.stderr.readline()
        self.process.stderr.readline()
        time.sleep(0.3)
        output.extend(self.output)
        self.output = []
    
        #print self.i
        #print "\n".join(output)
        return self.postprocess_output("\n".join(output))
        
    
    
    def close(self):
        self.running = False
        self.process.stdin.close()
        self.process.terminate()
    
    def __del__(self):
        self.close()
        
        
    def postprocess_output(self, output):
        
        #pattern that matches one error appearance
        pattern = 'ruleId="([^"]*)".*errorlength="([^"]*)"'
        #get a list of the error appearances
        errors = re.findall(pattern, output)

        #construct a vector of dictionaries with counts      
        atts = {}
        counts = {}
        
        for error_id, error_length in errors:
            error_label = "lgt_{0}".format(error_id).lower()
            error_count_label = "lgt_{0}_chars".format(error_id).lower()
            try:
                atts[error_label] += 1
                counts[error_count_label] += int(error_length)
            except KeyError:
                atts[error_label] = 1
                counts[error_count_label] = int(error_length)
                #print counts[error_count_label]
                        
        atts = dict([(k, str(v)) for (k,v) in atts.iteritems()])
        atts["lt_errors"] = str(len(errors))
        atts["lt_errors_chars"] = str(sum(counts.values()))
        counts = dict([(k, str(v)) for (k,v) in counts.iteritems()])
        atts.update(counts)
        #print atts
        return atts
        


class LanguageCheckerCmd(LanguageFeatureGenerator):
    
    def __init__(self, path, lang, params = {}, command_template= 'java -jar {path} -v -l {lang} -b --api',):
        self.lang = lang
    
    def add_features_batch(self, parallelsentences):
        process = subprocess.Popen(['commandline', 'test2.py'], shell=False, stdin=subprocess.PIPE)
#        process.communicate(parallelsentence.get_)
    
    
    def offline_process(self, filename_input, filename_output, existing_jcml):
        dataset = JcmlReader(existing_jcml).get_dataset()
        size = dataset.get_size()
        file_input = open(filename_input, 'r')
        file_content = file_input.read()
        att_vector = self._get_att_vector(file_content, size)
        dataset.add_attribute_vector(att_vector)
        
        Parallelsentence2Jcml(dataset.get_parallelsentences()).write_to_file(filename_output)

    
    def _get_att_vector(self, file_content, size):
        
        
        pattern = "\d*.\) Line (\d*), column \d*, Rule ID: (.*)\n"
        
        feature_entries = re.findall(pattern, file_content)
        feature_entries = [(int(key), value.replace("[", "_").replace("]", "_")) for  (key, value) in feature_entries]
        errors_per_sentence = {}
        possible_error_ids = set()
        #first make one list of error ids per sentence 
        for sentence_id , error_id in feature_entries:
            possible_error_ids.add(error_id)
            try:
                errors_per_sentence[sentence_id-1].append(error_id)
            except KeyError:
                errors_per_sentence[sentence_id-1] = [error_id]
                
        #construct a vector of dictionaries with counts
        vector_atts = []
        for i in range(0, size+1):
            atts = {}
            for error_id in possible_error_ids:
                error_label = "lgt_{0}".format(error_id).lower()
                atts[error_label] = 0  
            try:
                for error_id in errors_per_sentence[i]:
                    error_label = "lgt_{0}".format(error_id).lower()
                    atts[error_label] += 1
            except KeyError:
                pass
            vector_atts.append(atts)
    
        return vector_atts


if __name__ == '__main__':
    path = "/home/lefterav/taraxu_tools/LanguageTool-1.6/LanguageTool.jar"
    cmdfg = LanguageToolFeatureGenerator(path, 'en')
    from io_utils.input.jcmlreader import JcmlReader
    from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
    parallelsentences = JcmlReader("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/wmt00-test-devpart.orig.jcml").get_parallelsentences()
    annotated = cmdfg.add_features_batch(parallelsentences)
    cmdfg.close()
    Parallelsentence2Jcml(annotated).write_to_file("/home/lefterav/taraxu_data/selection-mechanism/ml4hmt/experiment/autoranking/4/training-sample.lt.jcml")
        
    
        