'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from time import sleep
from xml.sax.saxutils import escape
import sys
import xmlrpclib

from featuregenerator.blackbox.wsd import WSDclient
from featuregenerator.preprocessor import Tokenizer, Truecaser, Detokenizer,\
    Detruecaser
from mt.worker import Worker

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
        string = escape(string)
        response = False
        efforts = 0
        while response == False and efforts < 250:
            try:
                response = self.server.translate({'text': string})
                response = response
                efforts += 1
            except Exception as e:
                if "[Errno 111]" in str(e):
                    sys.stderr.write("Connection to MosesServer was refused, trying again in 20 secs...")
                    sleep(20)
                else:
                    raise e

        if response == False:
            sys.exit("Connection to MosesServer was refused for more than 5 minutes.")
        text = response['text']

        # it has been observed that some times the xmlrpc returns unicode, some others string
        # make it uniform
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        return text, response


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
        return text, result


class WsdMosesWorker(Worker):
    def __init__(self,
                 moses_url,
                 wsd_url,
                 source_language="en", target_language="de",
                 truecaser_model="/share/taraxu/systems/r2/de-en/moses/truecaser/truecase-model.3.en",
                 reverse=False):
        self.wsd_worker = WSDclient(wsd_url)
        self.moses_worker = MosesWorker(moses_url)
        self.tokenizer = Tokenizer(source_language)
        self.truecaser = Truecaser(source_language, truecaser_model)
        self.detokenizer = Detokenizer(target_language)
        self.detruecaser = Detruecaser(target_language)
    
    def translate(self, string):
        sys.stderr.write("Sending to WSD Analyzer\n")
        string = self.tokenizer.process_string(string)
        string = self.truecaser.process_string(string)
        wsd_source = self.wsd_worker.annotate(string)
        #kill invalid characters TODO: move to WSDclient
        wsd_source = wsd_source.decode('utf-8', errors='ignore').encode('utf-8')
        
        sys.stderr.write("Sending to WSD Moses:\n {}".format(wsd_source))
        moses_translation, _ = self.moses_worker.translate(wsd_source)
        moses_translation = self.detruecaser.process_string(moses_translation)
        moses_translation = self.detokenizer.process_string(moses_translation)
        return moses_translation, None