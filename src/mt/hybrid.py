'''
Created on 19 Apr 2016

@author: Eleftherios Avramidis
'''
import sys

import logging as log
from featuregenerator.preprocessor import Tokenizer, Truecaser
from featuregenerator.blackbox.wsd import WSDclient
from mt.lucy import LucyWorker, AdvancedLucyWorker
from mt.moses import MtMonkeyWorker, ProcessedMosesWorker, MosesWorker,\
    WsdMosesWorker
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
                 model=None):
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
                 model=None,
                 reverse=False):
       
        self.source_language = source_language
        self.target_language = target_language
        # load configuration files
        config = SafeConfigParser()
        log.error("Loading config files {}".format(configfiles))
        config.read(configfiles)
        self.workers = []
        self.reverse = reverse
        
        truecaser_model = config.get("Truecaser:{}".format(source_language), 'model')
        truecaser_model_target = config.get("Truecaser:{}".format(target_language), 'model')
        splitter_model = None
        if source_language == 'de':
            splitter_model = config.get("Splitter:{}".format(source_language), 'model')            

        tokenizer_protected = config.get("Tokenizer:{}".format(source_language), 'protected', None)

        # initialize Moses, even if not prefered engine, before Lucy cause it may be reused
        try:
            # get resources
            uri = config.get("Moses:{}-{}".format(source_language, target_language), "uri")
            self.moses_worker = ProcessedMosesWorker(uri, source_language, target_language, 
                                                     truecaser_model, splitter_model, 
                                                     tokenizer_protected)
        except:
            self.moses_worker = None
            
        self.lucy_worker = None
        self.lcm_worker = None
        self.wsd_worker = None

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
            
            if engine == "OldLucy" or (engine == "LcM" and not self.lucy_worker):
                params = dict(config.items("Lucy"))
                log.debug("Old Lucy starting with params: {}".format(params))
                self.lucy_worker = LucyWorker(source_language=source_language,
                                              target_language=target_language,
                                              **params)
                self.workers.append(self.lucy_worker)
                
                
            if engine == "LcM":
                uri = config.get("LcM:{}-{}".format(source_language, target_language), "uri")
                self.lcm_worker = ProcessedMosesWorker(uri, target_language, target_language, 
                                                       None, None,
                                                       tokenizer_protected, 
                                                       sentence_splitter=False)
                self.lcm_worker.name = "lcm"
                self.workers.append(self.lcm_worker)
                
            if engine == "WsdMoses":
                moses_url = config.get("WsdMoses:{}-{}".format(source_language, target_language), "moses_uri")
                wsd_url = config.get("WsdMoses:{}-{}".format(source_language, target_language), "wsd_uri")
                
                self.wsd_worker = WsdMosesWorker(moses_url, wsd_url, source_language, target_language, 
                                                 truecaser_model, reverse) 
                self.workers.append(self.wsd_worker)
                
            if engine == "NeuralMonkey":
                uri = config.get("NeuralMonkey:{}-{}".format(source_language, target_language), 
                                 "uri")
                self.neuralmonkey_worker = NeuralMonkeyWorker(uri, source_language, 
                                                              target_language, 
                                                              truecaser_model, splitter_model,
                                                              tokenizer_protected)
                self.workers.append(self.neuralmonkey_worker)
        
        self.selector = Autoranking(configfiles, model, source_language, 
                                    target_language, reverse=False)
        
        self.sentencesplitter = SentenceSplitter({'language': source_language})

        
        
    def translate(self, text, reconstruct="soft"):
        
        try:
            strings = self.sentencesplitter.split_sentences(text)
        except UnicodeDecodeError:
            try:
                text = unicode(text, errors='replace')
                strings = self.sentencesplitter.split_sentences(text)
            except:
                strings = [""]
        translation_strings = []
        ranked_parallelsentences = []
        descriptions = []
        
        for string in strings:
            #pool = Pool(processes=len(self.workers))
            #translations = pool.map(worker_translate, [(w, string) for w in self.workers])\
            
            translations = self.workers_translate(string)
            
            source = SimpleSentence(string, {})
            
            attributes = {"langsrc" : self.source_language, "langtgt" : self.target_language}
            parallelsentence = ParallelSentence(source, translations, attributes=attributes)
            translation_string, ranked_parallelsentence, description = self.selector.get_best_sentence(parallelsentence, 
                                                                                                       reconstruct=reconstruct)
            ranked_parallelsentences.append(ranked_parallelsentence)
            translation_strings.append(translation_string)
            descriptions.append(description)
        
        translation_string = " ".join(translation_strings)
        
        description = {}
        for i, descr in enumerate(descriptions):
            description[i] = descr 
        
        #TODO: maybe description should not be returned, as it is already contained in the ranked_sentence arguments
        return translation_string, ranked_parallelsentences, description     


    def workers_translate(self, string):
        lucy_string = ""
        translated_sentences = []
        for worker in self.workers:
            if worker.name == "lcm":
                #if lucy_string == "":
                #    raise Exception("Lucy should be in the order before LcM")
                translation = worker_translate(worker, lucy_string)
            else:
                translation = worker_translate(worker, string)
            if worker.name == "lucy":
                lucy_string = translation.get_string()
                log.debug("storing lucy output {}".format(lucy_string))
            translated_sentences.append(translation)
        return translated_sentences    

        
def worker_translate(worker, string):
    """
    Helper function that orders and fetches a translation from a worker
    @param worker: A machine translation worker
    @type worker: L{mt.worker.Worker}
    @param string: the text to be translated
    @type string: string
    @return: a bundled simple sentence object
    @rtype: L{sentence.sentence.SimpleSentence}
    """
    log.info("Translating with {}".format(worker.name))
    translated_sentence = worker.translate_sentence(string)
    translated_sentence.add_attribute("system", worker.name)
    log.debug("{} returned this string: {}".format(worker.name, translated_sentence.get_string()))
    return translated_sentence



    
class LcMWorker(Worker):
    def __init__(self,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",        
                 source_language="en", target_language="de",
                 config_files=[],
                 classifiername=None,
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-model.3.en",
                 splitter_model=None,
                 reverse=False):
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = ProcessedMosesWorker(lcm_url, source_language, target_language, 
                                               truecaser_model, splitter_model)
        self.tokenizer = Tokenizer(source_language)
        self.truecaser = Truecaser(source_language, truecaser_model)
        self.name = 'lcm'
    
    def translate(self, string):
        #string = self.tokenizer.process_string(string)
        #string = self.truecaser.process_string(string)
        
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
