'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

import logging as log
from requests.auth import HTTPBasicAuth
from xml.sax.saxutils import quoteattr
import re
import requests
import xml.etree.ElementTree as et

from mt.worker import Worker
from mt.moses import MtMonkeyWorker

#Template used for every Lucy request
TEMPLATE = """<task>
    <inputParams>
        <param name='TRANSLATION_DIRECTION' value='{langpair}'/>
        <param name='INPUT' value={input}/>
        <param name='SUBJECT_AREAS' value='{subject_areas}'/>
        <param name='MARK_ALTERNATIVES' value='{alternatives}'/>
        <param name='MARK_UNKNOWNS' value='{unknowns}'/>
        <param name='MARK_COMPOUNDS' value='{compounds}'/>
        <param name='CHARSET' value='UTF'/>
    </inputParams>
</task>"""

#Map iso language code to Lucy names
LANGMAP = {"en": "ENGLISH", 
           "de": "GERMAN",
           }

class LucyWorker(Worker):
    """
    A translation worker that communicates with the REST server wrapper of Lucy. 
    The default settings are already provided
    """
    def __init__(self, url, 
                 username="traductor", password="traductor", 
                 source_language="en", target_language="de",
                 subject_areas="(DP TECH CTV ECON)",
                 lexicon=None,
                 alternatives=False,
                 unknowns=False,
                 compounds=False,
                 ):
        
        self.langpair = "{}-{}".format(LANGMAP[source_language], 
                                       LANGMAP[target_language])
        
        self.url = url
        self.username = username
        self.password = password
        self.subject_areas = subject_areas
        self.lexicon = lexicon
        
        self.alternatives = alternatives
        self.unknowns = unknowns
        self.compounds = compounds
        

    def translate(self, string):
        alternatives = 1 if self.alternatives else 0
        unknowns = 1 if self.unknowns else 0
        compounds = 1 if self.compounds else 0
        
        data = TEMPLATE.format(langpair=self.langpair, 
                               input=quoteattr(string), 
                               subject_areas=self.subject_areas,
                               alternatives=alternatives,
                               unknowns=unknowns,
                               compounds=compounds
                               )
        headers = {'Content-type': 'application/xml'}
        auth = HTTPBasicAuth(self.username, self.password)
        log.debug("Lucy request: {}".format(data))
        response = requests.post(url=self.url, data=data, headers=headers, auth=auth)
        response.encoding = 'utf-8'
        # Interpret the XML response 
        try:        
            # get the xml node with the response
            try:
                xml = et.fromstring(response.text)
            except:
                xml = et.fromstring(response.text.encode('utf-8'))
            output = xml.findall("outputParams/param[@name='OUTPUT']")
            params = xml.findall("outputParams/param")
        except Exception as e:
            log.error("Got exception '{}' while parsing Lucy's response: {}".format(e, response.text.encode('utf-8')))
            return
        text = " ".join(t.attrib["value"] for t in output)
        
        if isinstance(text, unicode):
            text = text.encode('utf-8')        
            
        params = dict([(param.attrib["name"], param.attrib["value"]) for param in params])

        #for the moment draftly remove multiple translations and unknown words
        params["full_translation"] = text
        #text = re.sub("\<A\[(?P<alt>\w*)\|\w*\]\>", "\g<alt>", text)
        #text = re.sub("\<U\[(?P<unk>[^]]*)\]\>", "\g<unk>", text)
        #text = re.sub("\<M\[(?P<m>[^]]*)\]\>", "\g<m>", text)
        return text, params
 
 
class AdvancedLucyWorker(LucyWorker):   
    
    def __init__(self, moses_uri, **kwargs):
        self.moses = MtMonkeyWorker(moses_uri)
        kwargs["unknowns"] = True
        super(AdvancedLucyWorker, self).__init__(**kwargs)
    
    def translate(self, text):
        text, description = super(AdvancedLucyWorker, self).translate(text)
        text, unk_description = self._process_unknowns(text)
        description.update(unk_description)
        return text, description
    
    def _preprocess_menu_items(self, text):
        #tokenize the > sign
        text = re.sub("(?P<word>\w)>", "\g<word> >", text)
        
        tokens = text.split()
        separator_indices = [i for i in range(len(tokens)) if tokens[i]==">"]
        collected_chunk_indices = set()
        
        supplements = ["as", "..." , "for", "by", "to", "status"]
        
        for index in separator_indices:
            backwards_index = index - 1
            
            new_chunk = []
            while str.istitle(tokens[backwards_index]) \
            or tokens[backwards_index] in supplements:
                new_chunk.append(backwards_index)
                backwards_index-=1
            
            if new_chunk:
                collected_chunk_indices.add(new_chunk)
            
            forwards_index = index + 1
            new_chunk = []
            while str.istitle(tokens[forwards_index]) \
            or tokens[forwards_index] in supplements:
                new_chunk.append(forwards_index)
                forwards_index+=1
                
            if new_chunk:
                collected_chunk_indices.add(new_chunk)
        
        chunk_indices_list = sorted(list(collected_chunk_indices))
        
        i = 0
        new_tokens = []
        for token in tokens:
            tokens_chunk = [] 
            for chunk_indices in chunk_indices_list:
                start_index = chunk_indices[0]
                end_index = chunk_indices[1]
                if i > start_index and i < end_index+1:
                    tokens_chunk.append(token)
            
            i += 1
                
        return text
        
    
    def _process_unknowns(self, text):
        # get unknown tokens from Lucy output
        unknown_tokens = re.findall("<U\[([^]]*)\]>", text)
        description = {"unk_count" : len(unknown_tokens),
                       "unk_list": [],
                       "unk_replaced_list": []}
        replaced = 0 
        for unknown_token in unknown_tokens:
            translated_token, moses_description = self.moses.translate(unknown_token)
            #print moses_description
            score = moses_description['translation'][0]['translated'][0]['score']
            description["unk_list"].append(unknown_token)
            description["unk_replaced_list"].append((unknown_token, translated_token, score))
            text = text.replace("<U[{}]>".format(unknown_token), translated_token)
            if translated_token != unknown_token:
                replaced += 1
        description["unk_replaced"] = replaced
        return text, description
        
    