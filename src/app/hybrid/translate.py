import xmlrpclib
import logging as logger
from app.autoranking.application import Autoranking

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
        text = " ".join([t['text'] for t in result['translation']])
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
        print system2.translate("The solution to our problem has to go through several consultations and we also have to ask our friends, our family and our partners, before we reach a conclusion on this topic.")[0]

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

    

class SimpleTriangleTranslator(Worker):
    def __init__(self,
                 moses_url,
                 lucy_url, 
                 lcm_url,  
                 lucy_username="traductor", lucy_password="traductor",                
                 source_language="en", target_language="de",
                 configfilenames=[],
                 classifiername=None):
        self.selector =  Autoranking(configfilenames, classifiername)
        self.moses_worker = MtMonkeyWorker(url=moses_url)
        self.lucy_worker = LucyWorker(url=lucy_url,
                                      username=lucy_username, password=lucy_password,
                                      source_language=source_language,
                                      target_language=target_language) 
        self.lcm_worker = MtMonkeyWorker(url=lcm_url)
    
    def translate(self, string):
        moses_translation, _ = self.moses_worker.translate(string)
        lucy_translation, _ = self.lucy_worker.translate(string)
        lcm_translation, _ = self.lcm_worker.translate(lucy_translation)
        outputs_ordered = [moses_translation, lucy_translation, lcm_translation]
        rank = self.selector.rank(string, outputs_ordered)
        for rank_item, output in zip(rank, outputs_ordered):
            if rank_item==1:
                return output, None
            
            
import sys

if __name__ == '__main__':
    moses = SimpleTriangleTranslator(moses_url="http://134.96.187.247:7200", 
                                     lucy_url="http://msv-3251.sb.dfki.de:8080/AutoTranslateRS/V1.2/mtrans/exec",
                                     lcm_url="http://134.96.187.247:7200",
                                     source_language="en",
                                     target_language="de",
                                     )
    
    #TODO:
    #1. binarize LCM model.
    #2. start MtMonkey worker for LCM
    #3. Make sure LM servers are running in percival
    #4. Make sure all Featuregenerators work sentence-level
    #5. Define pipelines and find a way to load FeatureGenerators
    #6. Check that it works on the commandline
    #7. Wrap in XML-rpc service

    
    #moses.translate(sys.argv[1])
    moses.translate("Hello! How are you?")
    
    
    #text = system1.translate("This is a test, my dear.")
    #print system2.translate("The solution to our problem has to go through several consultations and we also have to ask our friends, our family and our partners, before we reach a conclusion on this topic.")[0]

