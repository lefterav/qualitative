#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import cgi

if __name__ == '__main__':
    pass



class Xmlhandler(ContentHandler):
    
    def __init__(self):
        
        #flags that show the current focus of the parsing
        self.is_parallelsentence = False 
        self.is_simplesentence = False
        
        self.ps_attributes={} #attributes of the parallel sentence
        self.ss_attributes={} #attributes of a simple sentence
        
        self.src=None
        self.tgt=[]
        self.ref=None
        
        self.ss_text=""
    
    def startElement(self, name, attrs):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        if name == 'judgedsentence':
            for att_name in attrs.getNames():
                self.ps_attributes[att] = attrs.getValue(att_name)
                self.is_parallelsentence = True
        elif name in ['src', 'tgt', 'ref']:
            for att_name in attrs.getNames():
                self.ss_attributes[att] = attrs.getValue(att_name)
                self.is_simplesentence = True
                
    def characters(self, ch):
        """
        The Parser will call this method to report each chunk of character data. 
        We use it to store the string of the simplesentence
        @param ch: character being parsed
        @type ch: str 
        """
        if self.is_simplesentence :
            self.ss_text += ch
    
    def endElement(self, name, attrs):
        """
        Signals the end of an element.
        Data stored in global vars of the class, time to create our objects and fire their processing
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        
        if name == 'src':
            self.src = SimpleSentence (self.ss_text, self.ss_attributes )
            self.ss_text = ""
        elif name =='tgt':
            self.tgt.append ( SimpleSentence (self.ss_text, self.ss_attributes ) )
            self.ss_text = ""
        elif name =='tgt':
            self.ref = SimpleSentence (self.ss_text, self.ss_attributes )
            self.ss_text = ""
        if name == "judgedsentence":
            parallelsentence = Parallelsentence ( self.src, self.tgt, self.ref , self.ps_attributes)
            
        
    
    