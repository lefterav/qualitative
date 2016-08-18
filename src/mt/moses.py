'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from time import sleep
from xml.sax.saxutils import escape
import sys
import xmlrpclib
import logging as log

from featuregenerator.blackbox.wsd import WSDclient
from featuregenerator.preprocessor import Tokenizer, Truecaser, Detokenizer,\
    Detruecaser, Normalizer, CompoundSplitter
from mt.worker import Worker
from featuregenerator.sentencesplitter import SentenceSplitter

class MosesWorker(Worker):
    """
    Wrapper class for Moses server
    @ivar server: the proxy to the Moses Server
    @type server: C{xmlrpclib.ServerProxy}
    """
    def __init__(self, uri, **kwargs):
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
        while response == False and efforts < 1250:
            try:
                response = self.server.translate({'text': string})
                response = response
                efforts += 1
            except Exception as e:
                log.error("{} \n Connection to MosesServer was refused, trying again in 20 secs...".format(e))
                sleep(20)
                log.error(e)

        if response == False:
            sys.exit("Connection to MosesServer was refused for more than 5 minutes.")
        text = response['text']

        # it has been observed that some times the xmlrpc returns unicode, some others string
        # make it uniform
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        return text, response
    

class ProcessedMosesWorker:
    """
    Wrapper class for Moses worker, that also takes care of pre-processing the given requests
    and post-processing the output
    @ivar worker: a worker that connects to a MT engine
    @type worker: L{Worker}
    @ivar sentencesplitter: the class for splitting sentences
    @type sentencesplitter: L{SentenceSplitter}
    @ivar preprocessors: a list of pre-processors
    @type preprocessors: list of L{Preprocessor}
    @ivar postprocessors: a list of post-processors
    @type postprocessors: list of L{Postprocessor}
    """
    def __init__(self, uri, source_language, target_language, 
                 truecaser_model, splitter_model=None, worker=MosesWorker, **kwargs):
        
        self.sentencesplitter = SentenceSplitter({'language': source_language})
        self.preprocessors = [Normalizer(language=source_language),
                              Tokenizer(language=source_language),
                              Truecaser(language=source_language, 
                                        model=truecaser_model),
                              ]
        if source_language == 'de' and splitter_model:
            self.preprocessors.append(CompoundSplitter(language=source_language,
                                                       model=splitter_model))
        self.postprocessors = [Detruecaser(language=target_language),
                               Detokenizer(language=target_language)
                               ]
        self.worker = worker(uri)
        
    def translate(self, string):
        strings = self.sentencesplitter.split_sentences(string)
        translated_strings = []
        responses = []
        
        for string in strings:
            for preprocessor in self.preprocessors:
                string = preprocessor.process_string(string)
            translated_string, response = self.worker.translate(string)
            print "output: ", translated_string, response
            for postprocessor in self.postprocessors:
                translated_string = postprocessor.process_string(translated_string)
            translated_strings.append(translated_string)
            responses.append(response)
        
        return " ".join(translated_strings), responses
            


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

        response = {}
        efforts = 0

        while not 'translation' in response and efforts < 250:
            try: 
                response = self.server.process_task(request)
                efforts += 1
                if 'error' in response: 
                    if "[Errno 111]" in response['error'] or "xml.parsers.expat.ExpatError" in response["error"]:
                        log.error("Connection to MosesServer was refused, trying again in 20 secs...")
                        sleep(20)
                    else:
                        raise Exception(response['error'])
                else:
                    if efforts > 1:
                        log.error("Server replied")
            except Exception as e:
                 log.error(e)
                 sleep(20)
                 pass

        if not 'translation' in response:
            sys.exit("Connection to MosesServer was refused for more than 5 minutes.")
        string_result = []
        for translation in response['translation']:
            for translated in translation['translated']:
                string_result.append(translated['text'])
        text = " ".join(string_result)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        return text, response


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
