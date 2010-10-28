'''
Created on 15 Οκτ 2010

@author: elav01
'''

import codecs
import xml.dom.minidom
from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
 

class XmlReader(object):
    '''
    classdocs
    '''

    def __init__(self, inputFilename):
        '''
        Constructor. Creates an XML object that handles the XML
        '''
        self.xmlObject = parse(inputFilename)
    
    def getAttributes(self):
        '''
        @return a list of the names of the attributes contained in the XML file
        '''
        return self.xmlObject.getXMLAttributes()
        
        
    def getSentences(self):
        '''
        @return: a list of ParallelSentence objects
        '''
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        newssentences = [] 
        for xmlEntry in sentenceList:
            srcXML = xmlEntry.getElementsByTagName('src')
            tgtXML = xmlEntry.getElementsByTagName('tgt')
            #refXML = xmlEntry.getElementsByTagName('ref')
            src = srcXML[0].childNodes[0].nodeValue.strip()
            tgt = map( lambda x: x.nodevalue.strip() , srcXML[0].childNodes )
            #ref = refXML[0].childNodes[0].nodeValue.strip()
            
            #Extract the XML features and attach them to the ParallelSentenceObject
            features = self.__read_features__(self.xmlObject, xmlEntry) 
            
            #create a new Parallesentence with the given content
            curJudgedSentence = ParallelSentence(src, tgt, "", features)
        
            newssentences.append(curJudgedSentence)
        return newssentences
    
    
    def __read_features__(self, xmlObject, xmlEntry):
        features = {}
        attributeKeys = xmlObject.getXMLAttributes()
        for attributeKey in attributeKeys:
            if attributeKey in xmlEntry.attributes.keys():
                features[attributeKey] = xmlEntry.attributes[attributeKey].value                     
        return features
        
    
    
    
        
        