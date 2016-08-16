'''
Created on 19 Apr 2016

@author: Eleftherios Avramidis
'''
import sys

from featuregenerator.preprocessor import Tokenizer, Truecaser
from featuregenerator.blackbox.wsd import WSDclient
from mt.lucy import LucyWorker
from mt.moses import MtMonkeyWorker
from mt.selection import Autoranking
from mt.worker import Worker

class HybridTranslator(Worker):
    def __init__(self, single_workers, worker_pipelines):
        self.workers = single_workers
        pass
    
    def translate(self, source_string):
        translated_string = None
        #TODO
        return translated_string 


class DummyTriangleTranslator():
    def __init__(self,
                 moses_url,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",                
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None):
        self.moses_worker = MtMonkeyWorker(moses_url)
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = MtMonkeyWorker(lcm_url)
        #print "Loaded systems"
    
    def translate(self, string):
        #print "Sending to Moses"
        moses_translation, _ = self.moses_worker.translate(string)
        #print "Sending to Lucy"
        lucy_translation, _ = self.lucy_worker.translate(string)
        #print "Sending to LcM"
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        #outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        return lucy_translation 

class SimpleTriangleTranslator(Worker):
    def __init__(self,
                 moses_url,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",                
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None,
                 reverse=False):
        self.selector =  Autoranking(config_files, classifiername, reverse)
        self.moses_worker = MtMonkeyWorker(moses_url)
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = MtMonkeyWorker(lcm_url)
    
    def translate(self, string):
        sys.stderr.write("Sending to Moses\n")
        #handle errors
        moses_translation, _ = self.moses_worker.translate(string)
        #moses_translation = "Moses translation"
        sys.stderr.write("Sending to Lucy\n")
        lucy_translation, _ = self.lucy_worker.translate(string)
        sys.stderr.write("Sending to LcM\n")
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        rank_strings, description = self.selector.rank_strings(string, outputs_ordered, reconstruct="soft")
        #print "Rank: ", rank_strings
        
        for rank_item, output in zip(rank_strings, outputs_ordered):
            if float(rank_item)==1:
                return output, description



    
    
class LcMWorker(Worker):
    def __init__(self,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",        
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None,
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-model.3.en",
                 reverse=False):
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = MtMonkeyWorker(lcm_url)
        self.tokenizer = Tokenizer(source_language)
        self.truecaser = Truecaser(source_language, truecaser_model)
    
    def translate(self, string):
        string = self.tokenizer.process_string(string)
        string = self.truecaser.process_string(string)
        
        sys.stderr.write("Sending to Lucy\n")
        lucy_translation, _ = self.lucy_worker.translate(string)
        sys.stderr.write("Sending to LcM\n")
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        return lcm_translation, None
    

class SimpleWsdTriangleTranslator(Worker):
    def __init__(self,
                 moses_url,
                 lucy_url, 
                 lcm_url,  
                 wsd_url,
                 lucy_username="traductor", lucy_password="traductor",        
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None,
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-model.3.en",
                 reverse=False):
        self.selector = Autoranking(config_files, classifiername, reverse)
        self.wsd_worker = WSDclient(wsd_url)
        self.moses_worker = MtMonkeyWorker(moses_url)
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.tokenizer = Tokenizer(source_language)
        self.truecaser = Truecaser(source_language, truecaser_model)
        self.lcm_worker = MtMonkeyWorker(lcm_url)
    
    def translate(self, string):
        sys.stderr.write("Sending to WSD Analyzer\n")
        string = self.tokenizer.process_string(string)
        string = self.truecaser.process_string(string)
        wsd_source = self.wsd_worker.annotate(string)
        sys.stderr.write("Sending to WSD Moses:\n {}".format(string))
        
        moses_translation, _ = self.moses_worker.translate(wsd_source)
        sys.stderr.write("Sending to Lucy\n")
        lucy_translation, _ = self.lucy_worker.translate(string)
        sys.stderr.write("Sending to LcM\n")
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        rank_strings, description = self.selector.rank_strings(string, outputs_ordered, reconstruct="soft")
        #print "Rank: ", rank_strings
        
        for rank_item, output in zip(rank_strings, outputs_ordered):
            if int(rank_item)==1:
                return output, description
