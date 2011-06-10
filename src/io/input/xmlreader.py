#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
"""


from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet
from xml.sax.saxutils import unescape
 

class XmlReader(object):
    """
    classdocs
    """

    def __init__(self, inputFilename):
        """
        Constructor. Creates an XML object that handles the XML
        """
        self.TAG_DOC = "jcml"
        self.TAG_SENT = "judgedsentence"
        self.TAG_SRC = "src"
        self.TAG_TGT = "tgt"
        self.TAG_REF = "ref"
        self.TAG_ANNOTATIONS = "annotations"
        self.TAG_ANNOTATION = "annotation"
        self.xmlObject = parse(inputFilename)
    
        
    def get_dataset(self):
        return DataSet(self.get_parallelsentences(), self.get_attributes(), self.get_annotations())
    
    
    def get_annotations(self):
        """
        @return a list with the names of the annotation layers that the corpus has undergone
        """
        try:
            annotations_xml_container = self.xmlObject.getElementsByTagName(self.TAG_ANNOTATIONS)
            annotations_xml = annotations_xml_container[0].getElementsByTagName(self.TAG_ANNOTATION)
            return [annotation_xml["name"] for annotation_xml in annotations_xml]
        except:
            print "File doesn't contain annotation information"
            return []
        
        

    
    
    def get_attributes(self):
        """
        @return a list of the names of the attributes contained in the XML file
        """
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG_DOC)
        sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG_SENT)
        attributesKeySet = set()
        
        for xmlEntry in sentenceList:
            for attributeKey in xmlEntry.attributes.keys():
                attributesKeySet.add(attributeKey)            
        return list(attributesKeySet)
    
    def length(self):
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG_DOC)
        return len(judgedCorpus[0].getElementsByTagName(self.TAG_SENT))
        
    def get_parallelsentences(self, start = None, end = None):
        """
        @return: a list of ParallelSentence objects
        """
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG_DOC)
        if not start and not end:
            sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG_SENT)
        else:
            sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG_SENT)[start:end]
        newssentences = [] 
        for xmlEntry in sentenceList:
            srcXML = xmlEntry.getElementsByTagName(self.TAG_SRC)
            tgtXML = xmlEntry.getElementsByTagName('tgt')
            refXML = xmlEntry.getElementsByTagName('ref')
            
            src = SimpleSentence (unescape(srcXML[0].childNodes[0].nodeValue.strip()) , self.__read_attributes__(srcXML[0]) )
            
            #Create a list of SimpleSentence objects out of the object
            tgt = map( lambda x: SimpleSentence(unescape(x.childNodes[0].nodeValue.strip()), self.__read_attributes__(x) )  , tgtXML ) 
            
            ref = SimpleSentence()
            try:    
                ref = SimpleSentence (unescape(refXML[0].childNodes[0].nodeValue.strip()) ,  self.__read_attributes__(refXML[0]))
            except LookupError:
                pass
            
            #Extract the XML features and attach them to the ParallelSentenceObject
            attributes = self.__read_attributes__(xmlEntry)
            
            #create a new Parallesentence with the given content
            curJudgedSentence = ParallelSentence(src, tgt, ref, attributes)
        
            newssentences.append(curJudgedSentence)
        return newssentences
    
    
    
    def __read_attributes__(self, xmlEntry):
        """
        @return: a dictionary of the attributes of the current sentence (name:value)
        """
        attributes = {}
        attributeKeys = xmlEntry.attributes.keys()
        for attributeKey in attributeKeys:
            attributes[attributeKey] = unescape(xmlEntry.attributes[attributeKey].value)                     
        return attributes
        
    