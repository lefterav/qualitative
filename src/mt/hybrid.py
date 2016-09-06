'''
Created on 19 Apr 2016

@author: Eleftherios Avramidis
'''
import sys

import logging as log
from featuregenerator.preprocessor import Tokenizer, Truecaser
from featuregenerator.blackbox.wsd import WSDclient
from mt.lucy import LucyWorker, AdvancedLucyWorker
from mt.moses import MtMonkeyWorker, ProcessedMosesWorker, MosesWorker
from mt.selection import Autoranking
from mt.worker import Worker
from ConfigParser import SafeConfigParser
from mt.neuralmonkey import NeuralMonkeyWorker
from multiprocessing import Pool
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from featuregenerator.sentencesplitter import SentenceSplitter

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
                 ranking_model=None):
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
        #lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        #outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        outputs_ordered = [moses_translation, lucy_translation]
        rank_strings, description = self.selector.rank_strings(string, outputs_ordered, reconstruct="soft")
        #print "Rank: ", rank_strings
        
        for rank_item, output in zip(rank_strings, outputs_ordered):
            if float(rank_item)==1:
                return output, description


class Pilot3Translator(SimpleTriangleTranslator):
    def __init__(self,
                 engines=["Moses", "Lucy", "NeuralMonkey"],
                 configfiles=[],
                 source_language="en",
                 target_language="de",
                 ranking_model=None):
       
        self.source_language = source_language
        self.target_language = target_language
        # load configuration files
        config = SafeConfigParser()
        log.error("Loading config files {}".format(configfiles))
        config.read(configfiles)
        self.workers = []
        

        # initialize Moses, even if not prefered engine, before Lucy cause it may be reused
        try:
            # get resources
            uri = config.get("Moses:{}-{}".format(source_language, target_language), "uri")
            truecaser_model = config.get("Truecaser:{}".format(source_language), 'filename')
            splitter_model = None
            if source_language == 'de':
                splitter_model = config.get("Splitter:{}".format(source_language), 'filename')            
            self.moses_worker = ProcessedMosesWorker(uri, source_language, target_language, 
                                                     truecaser_model, splitter_model)
        except:
            self.moses_worker = None

        for engine in engines:
        
            if engine == "Moses":
                self.workers.append(self.moses_worker)
                
            if engine == "Lucy":
                params = dict(config.items("Lucy"))
                if not self.moses_worker:
                    params["menu_translator"] = None
                self.lucy_worker = AdvancedLucyWorker(self.moses_worker,
                                                      source_language=source_language,
                                                      target_language=target_language,
                                                      **params)
                self.workers.append(self.lucy_worker)
                
            if engine == "LcM":
                uri = config.get("LcM:{}-{}".format(source_language, target_language), "uri")
                self.lcm_worker = ProcessedMosesWorker(uri, source_language, target_language, 
                                                       truecaser_model, splitter_model)
                
            if engine == "NeuralMonkey":
                uri = config.get("NeuralMonkey:{}-{}".format(source_language, target_language), 
                                 "uri")
                self.neuralmonkey_worker = NeuralMonkeyWorker(uri, source_language, 
                                                              target_language, 
                                                              truecaser_model, splitter_model)
                self.workers.append(self.neuralmonkey_worker)
        
        self.selector = Autoranking(configfiles, ranking_model, source_language, 
                                    target_language, reverse=False)
        
        self.sentencesplitter = SentenceSplitter({'language': source_language})

        
        
    def translate_with_selection(self, text, new_rank_name="rank_soft", reconstruct="soft"):
        
        strings = self.sentencesplitter.split_sentences(text)
        translation_strings = []
        ranked_parallelsentences = []
        descriptions = []
        
        for string in strings:
            pool = Pool(processes=len(self.workers))
            translations = pool.map(worker_translate, [(w, string) for w in self.workers])
            #translations = [worker_translate(w, string) for w in self.workers]
            
            source = SimpleSentence(string, {})
                    
            attributes = {"langsrc" : self.source_language, "langtgt" : self.target_language}
            parallelsentence = ParallelSentence(source, translations, attributes=attributes)
            ranked_parallelsentence, description = self.selector.get_ranked_sentence(parallelsentence, reconstruct=reconstruct, new_rank_name=new_rank_name)
            translation_string = ranked_parallelsentence.get_best_translation(new_rank_name=new_rank_name).get_string()
            
            ranked_parallelsentences.append(ranked_parallelsentence)
            translation_strings.append(translation_string)
            descriptions.append(description)
        
        translation_string = " ".join(translation_strings)
        if len(descriptions) > 1:
            description = {}
            for i, descr in enumerate(descriptions):
                description[i] = descr 
            
        return translation_string, ranked_parallelsentences, description     

    def translate(self, string, new_rank_name="rank_soft", reconstruct="soft"):
        translation_string, _, _ = self.translate_with_selection(string, new_rank_name=new_rank_name, reconstruct=reconstruct)
        return translation_string

        
def worker_translate(worker_string):
    """
    Helper function that orders and fetches a translation from a worker
    @param worker: A machine translation worker
    @type worker: L{mt.worker.Worker}
    @param string: the text to be translated
    @type string: string
    @return: a bundled simple sentence object
    @rtype: L{sentence.sentence.SimpleSentence}
    """
    worker, string = worker_string
    translated_sentence = worker.translate_sentence(string)
    translated_sentence.add_attribute("system", worker.name)
    return translated_sentence



    
class LcMWorker(Worker):
    def __init__(self,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",        
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None,
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-filename.3.en",
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
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-filename.3.en",
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
