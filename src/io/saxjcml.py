#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""


from xml.sax.saxutils import XMLGenerator
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence

class SaxJCMLProcessor(XMLGenerator):
    """
    Handles the generation of features over an XML object formatted as JCML. 
    It does processing every time a parallel sentence including its contents has been declared.
    Processing of any other XML type should follow this example.
    """
    
    def __init__(self, out, feature_generators = []):
        """
            @param out: file object to receive processed changes
            @param feature_generators: list of feature generators to be applied
        """
        
        #flags that show the current focus of the parsing
        self.is_parallelsentence = False 
        self.is_simplesentence = False
        #the following variables function as a buffer, that gets filled as the elements are being parsed
        #when elements are ended, then objects are created
        self.ps_attributes = {} #attributes of the parallel sentence
        self.ss_attributes = {} #attributes of a simple sentence
        
        self.src = None
        self.tgt = []
        self.ref = None
        
        self.ss_text = ""
        
        self.set_tags()
        
        self.feature_generators = feature_generators
        self._encoding = "utf-8"
        XMLGenerator._encoding = "utf-8"
        XMLGenerator._out = out
        
    def set_tags(self):
        """
        Handles the basic tags used for reading the simple XML format. 
        As tags are prone to changes, this can be done by changing values here, or overriding accordingly
        """
        self.TAG_DOC = "jcml"
        self.TAG_SENT = "judgedsentence"
        self.TAG_SRC = "src"
        self.TAG_TGT = "tgt"
        self.TAG_REF = "ref"
        self.TAG_ANNOTATIONS = "annotations"
        self.TAG_ANNOTATION = "annotation"
        
    def startDocument(self):
        XMLGenerator.startDocument(self)
        XMLGenerator.startElement(self, self.TAG_DOC, {})

    def endDocument(self):
        XMLGenerator.endElement(self, self.TAG_DOC)
        XMLGenerator.endDocument(self)
    
    def startElement(self, name, attrs=[]):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        if name == self.TAG_SENT:
            
            #empty up string and attribute buffer
            self.ss_text = u""
            self.ps_attributes = {}
            self.tgt = []
            for att_name in attrs.getNames():
                self.ps_attributes[att_name] = attrs.getValue(att_name)
            self.is_parallelsentence = True
            
        elif name in [self.TAG_SRC, self.TAG_TGT, self.TAG_REF]:
            
            #empty up string and attribute buffer
            self.ss_text = u""
            self.ss_attributes = {}
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
            self.ss_text = u"%s%s" % (self.ss_text, ch)
            
    
    def endElement(self, name):
        """
        Signals the end of an element.
        Data stored in global vars of the class, time to create our objects and fire their processing
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        
        #get rid of annoying leading spaces
        self.ss_text = self.ss_text.strip()
        
        #all of the elements have to be declared here
        #for each element, create the objects and clear "buffers"
        if name == self.TAG_SRC:
            self.src = SimpleSentence(self.ss_text, self.ss_attributes)
            self.ss_text = u""
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
            self.ss_text = u""
        elif name == self.TAG_SENT:
            #when the judged sentence gets closed, all previously inserted data have to be converted to objects 
            parallelsentence = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)

            #apply feature generators
            for fg in self.feature_generators:
                parallelsentence = fg.add_features_parallelsentence(parallelsentence)
                #parallelsentence.add_attributes( fg.get_features_parallelsentence(parallelsentence) )
            
            #print parallelsentence
            src = self.src
#            #print src.get_string()
#            for fg in self.feature_generators:
#                src = fg.add_features_src(src, parallelsentence)
#                #src.add_attributes( fg.get_features_src(src, parallelsentence) )
#            parallelsentence.set_source(src)

            #display modifications on output file
            XMLGenerator._write(self, "\n\t")
             
            XMLGenerator.startElement(self, name, parallelsentence.get_attributes())
                        
            XMLGenerator._write(self, "\n\t\t")
            XMLGenerator.startElement(self, self.TAG_SRC, src.get_attributes())
            XMLGenerator.characters(self, src.get_string())
            XMLGenerator.endElement(self, self.TAG_SRC)
            
            for tgt in parallelsentence.get_translations():
#                for fg in self.feature_generators:
#                    tgt = fg.add_features_tgt(tgt, parallelsentence)
#                    #tgt.add_attributes( fg.get_features_tgt(tgt, parallelsentence) )

                XMLGenerator._write(self, "\n\t\t")
                XMLGenerator.startElement(self, self.TAG_TGT, tgt.get_attributes())
                XMLGenerator.characters(self, tgt.get_string())
                XMLGenerator.endElement(self, self.TAG_TGT)
            
            XMLGenerator._write(self, "\n\t")
            XMLGenerator.endElement(self, name)
