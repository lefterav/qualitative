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
 

class TaraXUReader(object):
    """
    classdocs
    """

    def __init__(self, inputFilename):
        """
        Constructor. Creates an XML object that handles the XML
        """
        self.xmlObject = parse(inputFilename)
    
        
    def get_dataset(self):
        return DataSet(self.get_parallelsentences(), self.get_attributes())
    
    
    def get_attributes(self):
        """
        @return a list of the names of the attributes contained in the XML file
        """
        judgedCorpus = self.xmlObject.getElementsByTagName('doc')
        sentenceList = judgedCorpus[0].getElementsByTagName('sentence')
        attributesKeySet = set()
        
        for xmlEntry in sentenceList:
            for attributeKey in xmlEntry.attributes.keys():
                attributesKeySet.add(attributeKey)            
        return list(attributesKeySet)
    
    def length(self):
        judgedCorpus = self.xmlObject.getElementsByTagName('doc')
        return len(judgedCorpus[0].getElementsByTagName('sentence'))
        
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
    
    
    
    def __read_attributes__(self, xmlEntry):
        """
        @return: a dictionary of the attributes of the current sentence (name:value)
        """
        attributes = {}
        attributeKeys = xmlEntry.attributes.keys()
        for attributeKey in attributeKeys:
            attributes[attributeKey] = unescape(xmlEntry.attributes[attributeKey].value)
                        
        return attributes
        
    