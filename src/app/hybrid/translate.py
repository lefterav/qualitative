# -*- coding: utf-8 -*-

import xmlrpclib
import logging as logger
from app.autoranking.application import Autoranking
from featuregenerator.preprocessor import Normalizer, Tokenizer, Truecaser
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.blackbox.counts import LengthFeatureGenerator
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator
from featuregenerator.blackbox.ibm1 import AlignmentFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgAlignmentFeatureGenerator
from featuregenerator.blackbox.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from app.autoranking.bootstrap import ExperimentConfigParser
from featuregenerator.blackbox.wsd import WSDclient
import pickle

class Worker:
    """
    Abstract class for translation engine workers
    """
    def translate(self, string):
        """
    	Translate given string and return the result and any translation information
    	@param string: the string to be translated
    	@type string: string
    	@return translated_string, translation_info
    	@rtype: string, dict of (string, float) or (string, int) or (string, string)
    	"""
        raise NotImplementedError("This function needs to be implemented by a subclass of Worker")


class MosesWorker(Worker):
    """
    Wrapper class for Moses server
    """
    def __init__(self, uri, **params):
        """
    	Initialize connection to Moses server
    	@param uri: ip address or url of mosesserver followed by : and the port number
    	@type uri: string
    	"""
        #initialize XML rpc client
        #throw error if Moses server not started
        #self.server = xmlrpc.initialize("{}:{}".format(address, port))
        self.server = xmlrpclib.ServerProxy(uri)

    def translate(self, string):
        #send request to moses client
        response = self.server.translate({ 'text': 'test' })
        return response['text'], response


class MtMonkeyWorker(Worker):
    """
    Wrapper class for Moses server
    """
    def __init__(self, uri, **params):
        """
        Initialize connection to Moses server
        @param uri: ip address or url of mosesserver followed by : and the port number
        @type uri: string
        """
        #initialize XML rpc client
        #throw error if Moses server not started
        #self.server = xmlrpc.initialize("{}:{}".format(address, port))
        self.server = xmlrpclib.ServerProxy(uri)

    def translate(self, string):
        
        #try:
        request = {"action": "translate",
        "sourceLang": "en",
        "targetLang": "de",
        "text": string}
        result = self.server.process_task(request)
        string_result = []
        try:
            for translation in result['translation']:
                for translated in translation['translated']:
                    string_result.append(translated['text'])
            text = " ".join(string_result)
        except:
            text = ""
        #    logger.info('Worker alive check -- result: %s' % result)
        return text, result
        #except Exception, e:
        #    logger.info('Failed: Worker is busy (%s).' % e)
        #return False

import requests
from requests.auth import HTTPBasicAuth
from xml.sax.saxutils import escape
import xml.etree.ElementTree as et
import re

class LucyWorker(Worker):
    """
    """
    def __init__(self, url, 
                 username="traductor", password="traductor", 
                 source_language="en", target_language="de",
                 subject_areas="(DP TECH CTV ECON)",
                 ):
        
        langmap = {"en": "ENGLISH", 
                   "de": "GERMAN",
                   }
        
        self.langpair = "{}-{}".format(langmap[source_language], langmap[target_language])
        
        self.url = url
        self.username = username
        self.password = password
        self.subject_areas = subject_areas

    def translate(self, string):
        data = """<task>
        <inputParams>
            <param name='TRANSLATION_DIRECTION' value='{langpair}'/>
            <param name='INPUT' value='{input}'/>
            <param name='SUBJECT_AREAS' value='{subject_areas}'/>
            <param name='CHARSET' value='UTF'/>
        </inputParams>
        
        </task>""".format(langpair=self.langpair, input=escape(string), subject_areas=self.subject_areas)
        headers = {'Content-type': 'application/xml'}
        auth = HTTPBasicAuth(self.username, self.password)
        print data
        response = requests.post(url=self.url, data=data, headers=headers, auth=auth)
	response.encoding = 'utf-8'
        # Interpret the XML response 
        try:        
            # get the xml node with the response
            xml = et.fromstring(response.text)
            output = xml.findall("outputParams/param[@name='OUTPUT']")
            params = xml.findall("outputParams/param")
        except:
            logger.error("Lucy did not respond: {}".format(response.text))
            return
        text = " ".join(t.attrib["value"] for t in output)
        params = dict([(param.attrib["name"], param.attrib["value"]) for param in params])

	#for the moment draftly remove multiple translations and unknown words
	params["full_translation"] = text
	text = re.sub("\<A\[(?P<alt>\w*)\|\w*\]\>", "\g<alt>", text)
	text = re.sub("\<U\[(?P<unk>[^]]*)\]\>", "\g<unk>", text)
	text = re.sub("\<M\[(?P<m>[^]]*)\]\>", "\g<m>", text)
        return text, params
    
    def _handle_notation(self, string):
        re.sub()

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
                 configfilenames=[],
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
                 configfilenames=[],
                 classifiername=None):
        self.selector =  SystemSelector(configfilenames, classifiername)
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
        rank, description = self.selector.rank(string, outputs_ordered, reconstruct="soft")
        #print "Rank: ", rank
        
        for rank_item, output in zip(rank, outputs_ordered):
            if float(rank_item)==1:
                return output, description
            

class SimpleWsdTriangleTranslator(Worker):
    def __init__(self,
                 moses_url,
                 lucy_url, 
                 lcm_url,  
                 wsd_url,
                 lucy_username="traductor", lucy_password="traductor",                
                 source_language="en", target_language="de",
                 configfilenames=[],
                 classifiername=None):
        self.selector =  SystemSelector(configfilenames, classifiername)
        self.wsd_worker = WSDclient(wsd_url)
        self.moses_worker = MtMonkeyWorker(moses_url)
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = MtMonkeyWorker(lcm_url)
    
    def translate(self, string):
        sys.stderr.write("Sending to WSD Moses\n")
        wsd_source = self.wsd_worker.annotate(string)
        moses_translation, _ = self.moses_worker.translate(wsd_source)
        sys.stderr.write("Sending to Lucy\n")
        lucy_translation, _ = self.lucy_worker.translate(string)
        sys.stderr.write("Sending to LcM\n")
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        rank, description = self.selector.rank(string, outputs_ordered, reconstruct="soft")
        #print "Rank: ", rank
        
        for rank_item, output in zip(rank, outputs_ordered):
            if float(rank_item)==1:
                return output, description
            

class SystemSelector(Autoranking):
    def __init__(self, configfilenames, classifiername):
        """Autoranking
        Initialize the class.
        @param configfilenames: a list of annotation configuration files that contain
        the settings for all feature generators etc.
        @type configfilenames: list(str)
        @param classifiername: the filename of a picked classifier object
        @type classifiername: str
        """
        cfg = ExperimentConfigParser()
        for config_filename in configfilenames:
            cfg.read(config_filename)
        
        self.gateway = cfg.java_init()
        
        self.featuregenerators = self.initialize_featuregenerators(cfg)
        self.ranker = pickle.load(open(classifiername))
        self.source_language = cfg.get("general", "source_language")
        self.target_language = cfg.get("general", "target_language")
    
    def initialize_featuregenerators(self, cfg):
        """
        Initialize the featuregenerators that handle superficial analysis of given translations
        @param cfg: the loaded configuration object
        """
        source_language =  cfg.get("general", "source_language")
        target_language =  cfg.get("general", "target_language")
        
        src_parser = cfg.get_parser(source_language)
        tgt_parser = cfg.get_parser(target_language)

        langpair = (source_language, target_language)
        
        #attset_242_source = "lm_unk,l_tokens,berkeley-n,parse-VP,berkley-loglikelihood"
        #attset_242_target = "lm_prob,lm_unk,l_tokens,berkeley-n,parse-VP,berkley-loglikelihood,cfgal_unaligned,ibm1-score,ibm1-score-inv,l_avgoccurences,cfg_fulldepth,parse-comma,parse-dot,parse_S_depth_max,parse_S_depth_min,cfgpos_S-VP,cfgpos_end_VP-VZ,cfgpos_end_VP-VP,cfgpos_VP-VP,cfgpos_end_VP-VVINF,cfgpos_VP-VVINF,cfgpos_VP-VB,cfgpos_VP-VBZ,cfgpos_end_S-VVPP,cfgpos_VP-VBG,lt_UNPAIRED_BRACKETS,lt_DE_COMPOUNDS"

        featuregenerators = [
            Normalizer(source_language),
            Normalizer(target_language),
            Tokenizer(source_language),
            Tokenizer(target_language),
            
            src_parser,
            tgt_parser,
            
            ParserMatches(langpair),
            
            #truecase only for the language model
            Truecaser(source_language, cfg.get_truecaser_model(source_language)),
            Truecaser(target_language, cfg.get_truecaser_model(target_language)),
            
            cfg.get_lm(source_language),
            cfg.get_lm(target_language),    
                    
            AlignmentFeatureGenerator(cfg.get("ibm1:{}-{}".format(source_language, target_language), "lexicon"), 
                                      cfg.get("ibm1:{}-{}".format(target_language, source_language), "lexicon")),
            CfgAlignmentFeatureGenerator(),
            #LanguageToolSocketFeatureGenerator(target_language, self.gateway),
            CrossMeteorGenerator(target_language, self.gateway),
            LengthFeatureGenerator()
        ]
        
        return featuregenerators
 
  
import sys

if __name__ == '__main__':
    hybridsystem = SimpleTriangleTranslator(moses_url="http://134.96.187.247:7200", 
                                     lucy_url="http://msv-3251.sb.dfki.de:8080/AutoTranslateRS/V1.2/mtrans/exec",
                                     lcm_url="http://lns-87009.dfki.uni-sb.de:9300",
                                     source_language="de",
                                     target_language="en",
                                     configfilenames=sys.argv[2:],
                                     classifiername=sys.argv[1]
                                     )
    
    #TODO:
    #1. binarize LCM model.configfilenames=[],
                 #classifiername=None
    #2. start MtMonkey worker for LCM
    #3. Make sure LM servers are running in percival
    #4. Make sure all Featuregenerators work sentence-level
    #5. Define pipelines and find a way to load FeatureGenerators
    #6. Check that it works on the commandline
    #7. Wrap in XML-rpc service

    
    #hybridsystem.translate(sys.argv[1])
    print hybridsystem.translate("Ich habe ein iPad. Wie kann ich in Safari einen neuen Tab öffnen?")
    
    
    #text = system1.translate("This is a test, my dear.")
    #print system2.translate("The solution to our problem has to go through several consultations and we also have to ask our friends, our family and our partners, before we reach a conclusion on this topic.")[0]

