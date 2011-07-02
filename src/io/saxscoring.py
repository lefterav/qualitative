#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""


from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from xml.sax import handler

class SaxSystemScoring(handler.ContentHandler):
    """
    """
    
    def __init__(self, rank_attribute_name, outfilename, testset):
        """
        @param out: file object to receive processed changes
        @type out: file
        @param feature_generators: list of feature generators to be applied
        @type feature_generators: list
        """
        
        self.outfilename = outfilename
        self.rank_attribute_name = rank_attribute_name 
        self.testset = testset
        #flags that show the current focus of the parsing
        self.is_parallelsentence = False 
        self.is_simplesentence = False
        self.passed_head = False  #annotations declaration can only be done before any sentence has been declared
        #the following variables function as a buffer, that gets filled as the elements are being parsed
        #when elements are ended, then objects are created
        self.ps_attributes = {} #attributes of the parallel sentence
        self.ss_attributes = {} #attributes of a simple sentence
        
        self.src = None
        self.tgt = []
        self.ref = None
        self.annotations = []
        
        self.ss_text = ""
        
        self.set_tags()
        
        self._encoding = "utf-8"
        
        self.systems_performance = {}
        self.parallelsentences = 0
        
        
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
        pass

    def endDocument(self):
        outfile = open(self.outfilename, 'w')
        for system in self.systems_performance:
            self.systems_performance[system] = 1.00 * self.systems_performance[system] / self.parallelsentences
            entry = "dfki_parseconf\tde-en\t%s\t%s\t%01.4f\n" % (self.testset, system, self.systems_performance[system])
            outfile.write(entry)
        outfile.close()
    
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
            
            #add the newly produced feature generators to the heading of the generated file
            
            


            
        
        if name == self.TAG_ANNOTATION:
            if not self.passed_head:
                self.annotations.append(attrs.getValue("name"))
                
            else:
                print "Format error. Annotation must be declared in the beginning of the document"
        
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
            self.parallelsentences +=1
            rank_per_system = {}
            #first sort the ranks by system
            for target in parallelsentence.get_translations():
                system = target.get_attribute("system")
                rank = int(float(target.get_attribute(self.rank_attribute_name)))
                rank_per_system[system] = rank
            #then count the times a system performs as best
            for system in rank_per_system:
                if rank_per_system[system] == min(rank_per_system.values()):
                    try:
                        self.systems_performance[system] += 1
                    except KeyError:
                        self.systems_performance[system] = 1
            

                
        
