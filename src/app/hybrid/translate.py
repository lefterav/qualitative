import xmlrpclib
import logging as logger


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


class MtMonkey(Worker):
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

class LucyWorker(Worker):
    """
    """
    def __init__(self, url, username="traductor", password="traductor"):
        
        self.url = 'http://ES_search_demo.com/document/record/_search?pretty=true'
        self.username = username
        self.password = password
    
    def translate(self, string):
        data = """<task>
        <inputParams>
            <param name='TRANSLATION_DIRECTION' value='ENGLISH-GERMAN'/>
            <param name='INPUT' value='{}'/>
                <param name='SUBJECT_AREAS' value='(DP TECH CTV ECON)'/>
        </inputParams>
        </task>""".format(escape(string))
        headers = {'Content-type': 'application/xml'}
        auth = HTTPBasicAuth(self.username, self.password)
        print requests.post(url=self.url, auth=auth)
        response = requests.post(url=self.url, data=data,  headers=headers, auth=auth)
        print response
    

class HybridTranslator:
    def __init__(self, workers):
        self.workers = workers
        pass
    
    def translate(self, source_string):
        translated_string = None
        #TODO
        return translated_string 



if __name__ == '__main__':
    #system1 = MtMonkey("http://134.96.187.247:7200")
    #text = system1.translate("This is a test, my dear.")
    system2 = LucyWorker("http://msv-3251.sb.dfki.de:8080/AutoTranslateRS/V1.2/mtrans/exec")
    system2.translate("Testing this thing here.")

