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
 

class XmlReader(object):
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
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        attributesKeySet = set()
        
        for xmlEntry in sentenceList:
            for attributeKey in xmlEntry.attributes.keys():
                attributesKeySet.add(attributeKey)            
        return list(attributesKeySet)
    
    def length(self):
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        return len(judgedCorpus[0].getElementsByTagName('judgedsentence'))
        
    def get_parallelsentences(self, start = None, end = None):
        """
        @return: a list of ParallelSentence objects
        """
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        if not start and not end:
            sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        else:
            sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')[start:end]
        newssentences = [] 
        for xmlEntry in sentenceList:
            srcXML = xmlEntry.getElementsByTagName('src')
            tgtXML = xmlEntry.getElementsByTagName('tgt')
            refXML = xmlEntry.getElementsByTagName('ref')
            
            src = SimpleSentence ( srcXML[0].childNodes[0].nodeValue.strip() , self.__read_attributes__(srcXML[0]) )
            
            #Create a list of SimpleSentence objects out of the object
            tgt = map( lambda x: SimpleSentence ( x.childNodes[0].nodeValue.strip(), self.__read_attributes__(x) )  , tgtXML ) 
            
            ref = SimpleSentence()
            try:    
                ref = SimpleSentence ( refXML[0].childNodes[0].nodeValue.strip() ,  self.__read_attributes__(refXML[0]))
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
            attributes[attributeKey] = xmlEntry.attributes[attributeKey].value                     
        return attributes
        
    