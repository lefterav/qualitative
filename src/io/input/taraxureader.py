#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
"""


from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from xml.sax.saxutils import unescape
from xmlreader import XmlReader

class TaraXUReader(XmlReader):
    """
    classdocs
    """

    def __init__(self, inputFilename):
        """
        Constructor. Creates an XML object that handles the XML
        """
        self.TAG_DOC = "doc"
        self.TAG_SENT = "sentence"
        self.TAG_SRC = "source"
        self.TAG_TGT = "target"
        self.TAG_REF = "reference"
        self.TAG_ANNOTATIONS = "annotations"
        self.TAG_ANNOTATION = "annotation"
        self.xmlObject = parse(inputFilename)
    
    

    def get_parallelsentences(self, start = None, end = None):
        """
        @return: a list of ParallelSentence objects
        """
        judgedCorpus = self.xmlObject.getElementsByTagName('doc')
        langsrc = judgedCorpus[0].attributes["source_language"].value
        langtgt = judgedCorpus[0].attributes["target_language"].value
        if not start and not end:
            sentenceList = judgedCorpus[0].getElementsByTagName('sentence')
        else:
            sentenceList = judgedCorpus[0].getElementsByTagName('sentence')[start:end]
        newssentences = [] 
        for xmlEntry in sentenceList:
            srcXML = xmlEntry.getElementsByTagName('source')
            tgtXML = xmlEntry.getElementsByTagName('target')
            refXML = xmlEntry.getElementsByTagName('reference')
            
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
            attributes["langsrc"] =  langsrc
            attributes["langtgt"] =  langtgt
                        
            #create a new Parallesentence with the given content
            curJudgedSentence = ParallelSentence(src, tgt, ref, attributes)
            
            
            newssentences.append(curJudgedSentence)
        return newssentences
    
    

        
    