#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""


from xml.sax.saxutils import XMLGenerator
from xml.sax import ContentHandler
from io.input.genericreader import GenericReader
from io.output.xmlwriter import GenericWriter
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import StringIO
from copy import deepcopy


class SaxWrapper(ContentHandler):
    """
    Abstract SAX wrapper to facilitate use of older minidom processors.
    """
    i = 0
    
    def __init__(self, element_focus, reader = GenericReader, writer = GenericWriter, filename_out = ""):
        """
        """
        
        self.element_focus = element_focus
        self.recording = False
        self.buffer_generator = None
        self.nodetext = u""
        self.reader = reader
        self.writer = writer
        self.stringbuffer = None
        self.parallelsentences = []
        self.filename_out = filename_out
        self.tobeparsedonce = []
        #self.file_out = open(filename_out, 'w')
        #self.finalgenerator = XMLGenerator(self.file_out, encoding="utf8")
    
    
    def startElement(self, name, attrs=[]):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        
        
        if name == self.element_focus:
            self.recording = True
            self.stringbuffer = StringIO.StringIO()
            self.buffer_generator = XMLGenerator(self.stringbuffer, encoding="utf8")
            for (element_name, element_attrs) in self.tobeparsedonce:
                self.buffer_generator.startElement(element_name, element_attrs)
        if self.recording:
            self.buffer_generator.startElement(name, attrs)
        else:
            self.tobeparsedonce.append((name, attrs))
            #self.finalgenerator.startElement(name, attrs)
        
        
                
    def characters(self, ch):
        """
        The Parser will call this method to report each chunk of character data. 
        We use it to store the string 
        @param ch: character being parsed
        @type ch: str 
        """
        if self.recording:
            self.nodetext = u"%s%s" % (self.nodetext, ch)
        else:
            #self.finalgenerator.characters(ch)
            pass
            
    
    def endElement(self, name):
        """
        Signals the end of an element.
        Data stored in global vars of the class, time to create our objects and fire their processing
        @param name: the name of the element
        @type name: str 
        @param attrs: of the element type as a string and the attrs parameter holds an object of the Attributes interface containing the attributes of the element.
        @type attrs: Attributes
        """
        
        if not self.recording:
            #self.finalgenerator.endElement(name)
            self.tobeparsedonce.pop()
            pass
        else:
            self.buffer_generator.characters(self.nodetext)
            self.buffer_generator.endElement(name)
            self.nodetext = u""
            
            if name == self.element_focus:
                self.recording = False
                tobeclosed = deepcopy(self.tobeparsedonce)
                tobeclosed.reverse()
                for (element_name, element_attrs) in tobeclosed:
                    self.buffer_generator.endElement(element_name)
                self.stringbuffer.flush()
                #self.reader = GenericReader
                string = self.stringbuffer.getvalue()
                
                reader = self.reader(string, True, True)
                parallelsentence = reader.get_parallelsentences()[0]
                #parallelsentence_xmlstring = self.writer().get_parallelsentence_string(parallelsentence)
                #self.finalgenerator._write(parallelsentence_xmlstring)
                self.i += 1
                print self.i
                self.parallelsentences.append(parallelsentence)
                self.stringbuffer.close()
                self.stringbuffer = None
                
    
    def endDocument(self):
        self.writer(self.parallelsentences).write_to_file(self.filename_out)
        #self.file_out.close()
        #pass
                
