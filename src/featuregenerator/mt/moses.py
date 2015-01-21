'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''
import xmlrpclib
from engine import MtEngine

class MtMonkeyWorker(MtEngine):
    def __init__(self, source_language, target_language, url):
        self.source_language = source_language
        self.target_language = target_language
        self.server = xmlrpclib.ServerProxy(url)
        
    def translate_string(self, string):
        response = self.server.translate({ 'text': string })
        text = response['text']
        features = response
        

               