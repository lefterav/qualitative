# -*- coding: utf-8 -*-
'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

from requests.auth import HTTPBasicAuth
from urllib import quote, unquote
from xml.sax.saxutils import quoteattr
import HTMLParser
import logging as log
import re
import requests
import xml.etree.ElementTree as et

from mt.worker import Worker
from mt.moses import MtMonkeyWorker
from featuregenerator.preprocessor import Normalizer, Tokenizer
from argparse import SUPPRESS

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
 
def encode_chunk_simple(tokens):
    text = " ".join(tokens)
    return "$menu::{}$".format(quote(text))

def encode_chunk_quoted(tokens):
    text = " ".join(tokens)
    # remove existing quotes, since we are going to add them anyway
    text = text.replace('"', '')
    items = text.split(" > ")
    # put quotes before and after every > separator
    quoted_text = '" > "'.join(["{}".format(item) for item in items])
    # put quotes before and after every menu chunk
    return '$menu::"{}"$'.format(quote(quoted_text))


class AdvancedLucyWorker(LucyWorker):   
    
    def __init__(self, moses_uri, 
                 unknowns=True,
                 menu_items=True,
                 menu_quotes=False, # or 'quoted'
                 menu_translator="Moses", 
                 suppress_where_it_says=False,
                 normalize=True, **kwargs):
        
        self.moses = MtMonkeyWorker(moses_uri)
        
        # normalizer fixes punctuation like weird quotes
        if normalize:
            self.normalizer = Normalizer(kwargs["source_language"])
        else:
            self.normalizer = None
            
        
            
            
        self.tokenizer = Tokenizer(kwargs["source_language"])
            
        # should Lucy annotate unknown words?
        kwargs["unknowns"] = unknowns
        self.unknowns = unknowns
        self.suppres_where_it_says = suppress_where_it_says
        # specify whether the menu items should be handled
        self.menu_items = menu_items
        self.menu_translator = menu_translator
        self.menu_quotes = menu_quotes
        
        super(AdvancedLucyWorker, self).__init__(**kwargs)
    
    def translate(self, text):
        
        description = {}
        
        if self.normalizer:
            text = self.normalizer.process_string(text)
        
        if self.suppres_where_it_says:
            text = text.replace("where it says", "on")
        
        if self.menu_items:
            text, menu_description = self._preprocess_menu_items(text, self.menu_quotes)
            description.update(menu_description)
        
        text, lucy_description = super(AdvancedLucyWorker, self).translate(text)
        description.update(lucy_description)
        
        if self.menu_items:
            text = self._postprocess_menu_items(text, self.menu_translator)
        
        # if Lucy has annotated unknown words, we should pass them to moses
        if self.unknowns:
            text, unk_description = self._process_unknowns(text)
            description.update(unk_description)
        return text, description
    
    def _preprocess_menu_items(self, text, menu_quotes=False):
        
        # select the corresponding function, depending on we want
        # items between the > signs to be in quotes
        if menu_quotes:
            process_chunk = encode_chunk_quoted
        else:
            process_chunk = encode_chunk_simple
        
        # tokenize the > sign
        text = re.sub("(?P<word>\w)>", "\g<word> >", text)
        
        # collect metadata from the translation and processing steps
        description = {}
        
        # typical menu words that are not capitalized
        supplements = ["as", "...", "…" , "for", "by", "status"]
        
        # identifiy the positions of the > separators
        tokens = text.split()
        separator_indices = [i for i in range(len(tokens)) if tokens[i]==">"]

        # gather capitalized chunks before every > separator
        backwards_chunk_indices = set()
        for index in separator_indices:
            backwards_index = index - 1
            new_chunk = []
            while backwards_index >= 0 \
            and (str.istitle(tokens[backwards_index][:2]) \
            or tokens[backwards_index] in supplements):
                new_chunk.append(backwards_index)
                backwards_index-=1
            
            if new_chunk:
                backwards_chunk_indices.add((new_chunk[-1], new_chunk[0]))
                
        # gather capitalized chunks after every > separator
        forward_chunk_indices = set()
        forward_chunk_dict = {}        
        for index in separator_indices:
            forwards_index = index + 1
            new_chunk = []
            while forwards_index < len(tokens) \
            and (str.istitle(tokens[forwards_index][:2]) \
            or tokens[forwards_index] in supplements):
                new_chunk.append(forwards_index)
                forwards_index+=1
                
            if new_chunk:
                forward_chunk_indices.add((new_chunk[0], new_chunk[-1]))
                forward_chunk_dict[new_chunk[0]] = (new_chunk[0], new_chunk[-1])
        
        description["menu_items"] = len(backwards_chunk_indices.union(forward_chunk_indices))
        
        # join adjacent chunks
        joined_chunks = []
        new_joined_chunk = []
        for chunk_start, chunk_end in sorted(list(backwards_chunk_indices)):
            forward_chunk_start = chunk_end + 2
            try:
                forward_chunk_start, forward_chunk_end = forward_chunk_dict[forward_chunk_start]
            except:
                continue
            if not (chunk_start, chunk_end) in forward_chunk_indices:
                new_joined_chunk.append(chunk_start)
            if not (forward_chunk_start, forward_chunk_end) in backwards_chunk_indices:
                new_joined_chunk.append(forward_chunk_end)
                joined_chunks.append(new_joined_chunk)
                new_joined_chunk = []
                
        index = 0
        
        description["menus"] = len(joined_chunks)
        
        # finally go through the original string token by token
        # and assemble a new string where item menus are replaced by
        # encoded placeholders 
        final_tokens = []
        for index, token in enumerate(tokens):
            found_in_chunk = False
            start_of_chunk = False
            for chunk_indices in joined_chunks:
                try:
                    chunk_start, chunk_end = chunk_indices
                except ValueError:
                    continue
                if index == chunk_start:
                    start_of_chunk = True
                    break
                elif (index > chunk_start and index <= chunk_end):
                    found_in_chunk = True
                    break
            if start_of_chunk:
                final_tokens.append(process_chunk(tokens[chunk_start:chunk_end+1]))
            elif not found_in_chunk:
                final_tokens.append(token)
                
        return " ".join(final_tokens), description
    
    
    def _postprocess_menu_items(self, text, translator="Moses"):
        menu_chunks = re.findall("\$menu::([^$]*)\$", text)
        log.debug("Post-processing {} menu chunks".format(len(menu_chunks)))
        for chunk in menu_chunks:
            # break the placeholder into normal characters 
            clean_chunk = unquote(chunk)
             
            #clean_chunk = self.tokenizer.process_string(clean_chunk)
            # get the translation from Moses (or lucy?)
            if translator == "Moses":
                #log.debug("Sending clean menu chunk to Moses: '{}'".format(clean_chunk))
                chunk_translation, _ = self.moses.translate(clean_chunk)
                #log.debug("Moses returned menu chunk: '{}'".format(chunk_translation))
            else:
                chunk_translation = []
                for item in clean_chunk.split(" > "):
                    item_translation, _ = super(AdvancedLucyWorker, self).translate(item)
                    chunk_translation.append(item_translation)
                chunk_translation = " > ".join(chunk_translation)
            
            # unescape things like &gt;
            #chunk_translation = HTMLParser.HTMLParser().unescape(chunk_translation)
            # put the translation back in the position of the placeholder
            text = text.replace("$menu::{}$".format(chunk), chunk_translation)
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
        
    