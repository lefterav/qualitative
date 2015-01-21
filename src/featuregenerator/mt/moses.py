'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''
import xmlrpclib
from engine import MtEngine
from sentence.sentence import SimpleSentence

class MtMonkeyWorker(MtEngine):
    def __init__(self, source_language, target_language, url):
        self.source_language = source_language
        self.target_language = target_language
        self.server = xmlrpclib.ServerProxy(url)
        
    def translate_string(self, string):
        response = self.server.process_task({ 'text': string,
                                             'action': 'translate',
                                             'sourceLang': self.source_language,
                                             'targetLang': self.target_language,
                                             'alignmentInfo': True,
                                             'nBestSize': 10,
                                             })
        translated = response['translated']
        source_tokenized = response['src-tokenized']
        translations = ()
        for translated_entry in translated:
            translated_text = translated_entry['text']
            translated_score = translated_entry['score']
            translated_tokenized = translated_entry['tokenized']
            translated_alignment = translated_entry['alignment-raw']
            #process alignment-raw
            #find a way to continue working with both tokenized and untokenized text
            translation = SimpleSentence(translated_text)
            translations.append(translation)
            
        

               