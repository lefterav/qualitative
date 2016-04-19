'''
Created on 26 Nov 2014

@author: Eleftherios Avramidis
'''

import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as et
import re
from mt.worker import Worker
from xml.sax.saxutils import quoteattr
import logging as log


class LucyWorker(Worker):
    """
    A translation worker that communicates with the REST server wrapping Lucy. 
    The default settings are already provided
    """
    def __init__(self, url, 
                 username="traductor", password="traductor", 
                 source_language="en", target_language="de",
                 subject_areas="(DP TECH CTV ECON)",
                 lexicon=None
                 ):
        
        langmap = {"en": "ENGLISH", 
                   "de": "GERMAN",
                   }
        
        self.langpair = "{}-{}".format(langmap[source_language], langmap[target_language])
        
        self.url = url
        self.username = username
        self.password = password
        self.subject_areas = subject_areas
        self.lexicon = lexicon

    def translate(self, string):
        data = """<task>
        <inputParams>
            <param name='TRANSLATION_DIRECTION' value='{langpair}'/>
            <param name='INPUT' value={input}/>
            <param name='SUBJECT_AREAS' value='{subject_areas}'/>
            <param name='CHARSET' value='UTF'/>
            <param name='MARK_ALTERNATIVES' value='0'/>
            <param name='MARK_UNKNOWNS' value='0'/>
            <param name='MARK_COMPOUNDS' value='0'/>
            <param name='CHARSET' value='UTF'/>
        </inputParams>
        
        </task>""".format(langpair=self.langpair, 
                          input=quoteattr(string), 
                          subject_areas=self.subject_areas,
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
        params = dict([(param.attrib["name"], param.attrib["value"]) for param in params])

        #for the moment draftly remove multiple translations and unknown words
        params["full_translation"] = text
        text = re.sub("\<A\[(?P<alt>\w*)\|\w*\]\>", "\g<alt>", text)
        text = re.sub("\<U\[(?P<unk>[^]]*)\]\>", "\g<unk>", text)
        text = re.sub("\<M\[(?P<m>[^]]*)\]\>", "\g<m>", text)
        return text, params
    