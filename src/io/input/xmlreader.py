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
        Constructor
        '''
        self.xmlObject = parse(inputFilename)
        
    def getSentences(self):
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
            features = self.__read_features__(self.xmlObject, xmlEntry) 
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
        
    
    
    
        
        