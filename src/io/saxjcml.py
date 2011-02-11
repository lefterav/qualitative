#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""

from xml.sax.handler import ContentHandler
from xml.sax.saxutils import XMLGenerator
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence


import cgi

if __name__ == '__main__':
    pass


class SaxJCMLProcessor(XMLGenerator):
    """
        Handles the generation of features over an XML object formatted as JCML. 
        It does processing every time a parallel sentence including its contents has been declared.
        Processing of any other XML type should follow this example.
    """
    
    def __init__(self,  out, feature_generators=[]):
        
        #flags that show the current focus of the parsing
        self.is_parallelsentence = False 
        self.is_simplesentence = False
        
        self.ps_attributes={} #attributes of the parallel sentence
        self.ss_attributes={} #attributes of a simple sentence
        
        self.src=None
        self.tgt=[]
        self.ref=None
        
        self.ss_text=""
        
        self.feature_generators = feature_generators
        XMLGenerator._encoding = "UTF-8"
        XMLGenerator._out = out
        
    def startDocument(self):
        XMLGenerator.startDocument(self)
    
    def startElement(self, name, attrs=[]):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        if name == 'judgedsentence':
            for att_name in attrs.getNames():
                self.ps_attributes[att_name] = attrs.getValue(att_name)
                self.is_parallelsentence = True
        elif name in ['src', 'tgt', 'ref']:
            for att_name in attrs.getNames():
                self.ss_attributes[att_name] = attrs.getValue(att_name)
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
    
    def endElement(self, name, attrs=[]):
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
            #XMLGenerator.startElement(self, name, self.ss_attributes)
            #XMLGenerator.characters(self, self.ss_text)
            #XMLGenerator.endElement(self, name)
            self.ss_text = ""
        elif name =='tgt':
            self.tgt.append ( SimpleSentence (self.ss_text, self.ss_attributes ) )
            #XMLGenerator.startElement(self, name, self.ss_attributes)
            #XMLGenerator.characters(self, self.ss_text)
            #XMLGenerator.endElement(self, name)
            self.ss_text = ""
        if name == "judgedsentence":
            parallelsentence = ParallelSentence ( self.src, self.tgt, self.ref , self.ps_attributes)
            
            for fg in self.feature_generators:
                annotated_parallelsentence = fg.add_features_parallelsentence(parallelsentence)
            #print annotated_parallelsentence.get_source().get_string() , annotated_parallelsentence.get_attributes()
            
            
            XMLGenerator.startElement(self, name, annotated_parallelsentence.get_attributes())
            src = parallelsentence.get_source()
            XMLGenerator.startElement("src", src.get_attributes())
            XMLGenerator.characters(self, src.get_string())
            XMLGenerator.endElement("src")
            for tgt in self.tgt:
                XMLGenerator.startElement("tgt", tgt.get_attributes())
                XMLGenerator.characters(self, tgt.get_string())
                XMLGenerator.endElement("tgt")
            
            #XMLGenerator.characters(self, self.ss_text)
            XMLGenerator.endElement(self, name)
            #saxwriter.print( annotated_parallelsentence )