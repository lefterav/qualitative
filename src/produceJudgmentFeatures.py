# -*- coding: utf-8 -*-

'''
    This script reads the XML-formatted data from pairwise system comparisons and
    adds various features based on various linguistic characteristics of each parallel sentence.  
'''


import sys
import codecs
import xml.dom.minidom
from xml.dom.minidom import parse
from nltk import word_tokenize

class JudgedSentence:
    def __init__(self, xmlEntry):
        self.xmlObject = xmlEntry
        srcXML = xmlEntry.getElementsByTagName('src')
        tgtXML = xmlEntry.getElementsByTagName('tgt')
        self.src = srcXML[0].childNodes[0].nodeValue.strip()
        return None
    def getOutput(self):
        return self.xmlObject

    def addSentenceLengthFeatures(self):
        length = len(word_tokenize(self.src))
        
        self.xmlObject.setAttribute('src-length' , str(length))
        
        srcShort = '0'
        srcLong = '0'
        srcToolong = '0'
        if length<10:
            srcShort = '1'
        elif length>25:
            srcLong = '1'
            if length>50:
                srcToolong = '1'
        
        self.xmlObject.setAttribute('src-short' , srcShort)
        self.xmlObject.setAttribute('src-long' , srcLong)
        self.xmlObject.setAttribute('src-toolong' , srcToolong)
        
        
        return None
    
        
        
    

'''
    Models the behaviour of a corpus containing judged translations and features
'''
class JudgedSet :
    '''
        Initialiaze the set, but parsing the XML input given in the parameters
        @param inputFilename: The filename of a text file formatted in JCML/XML
        @param outputFilename: The filename of the text where the outcome will be stored 
    '''
    def __init__(self, inputFilename, outputFilename):
        self.xmlObject = parse(inputFilename)
        self.outputFilename = outputFilename
        return None
    
    def flush(self):
        file_object = codecs.open(self.outputFilename, 'w', 'utf-8')
        file_object.write(self.xmlObject.toprettyxml())
        file_object.close()  
    '''
        Adds a set of features into the XML object. Features may vary
        
    '''
    def addFeatures(self):
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        for xmlEntry in sentenceList:
            curJudgedSentence = JudgedSentence(xmlEntry)
            curJudgedSentence.addSentenceLengthFeatures()
            #self.enumNominalFeatures(['testset'])
        return None


    '''
        Returns a list of all the attributes of the judgedsentences
    '''
    def getXMLAttributes(self):
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        attributesKeySet = set()
        
        for xmlEntry in sentenceList:
            for attributeKey in xmlEntry.attributes.keys():
                attributesKeySet.add(attributeKey)            
        return list(attributesKeySet)
    
    
    
    '''
        Gets a list of attribute names which have string values and makes sure they are converted to integers 
    '''
    def enumNominalFeatures(self,givenNominalAttributeList):
        judgedCorpus = self.xmlObject.getElementsByTagName('jcml')
        sentenceList = judgedCorpus[0].getElementsByTagName('judgedsentence')
        
        
        #create an empty dic for every given attribute key
        #each entry in the dic will point to a set with the possible values of the attr key
        seenAttributeValues = {}
        
        #first parse to get the values domain per nominal attribute in a set
        for xmlEntry in sentenceList:
            #get the attributes of this list
            for attributeKey in givenNominalAttributeList:
                #get the value of the attribute only if it exists in this sentence
                if attributeKey in xmlEntry.attributes.keys():
                    attributeValue = xmlEntry.attributes[attributeKey]
                    #make sure a set exists
                    if not seenAttributeValues.has_key(attributeKey):
                        seenAttributeValues[attributeKey] = set()
                    seenAttributeValues[attributeKey].add(attributeValue)
        
        #convert into list
        for attributeKey in givenNominalAttributeList:
            seenAttributeValues[attributeKey]=list(seenAttributeValues[attributeKey])
    
        #second parse to replace values with numerical ones
        for xmlEntry in sentenceList:
            #get the attributes of this list
            for attributeKey in givenNominalAttributeList:
                #deal the value of the attribute only if it exists in this sentence
                if attributeKey in xmlEntry.attributes.keys():
                    #replace value with its numerical index in the values' domain set 
                    attributeValue = xmlEntry.attributes[attributeKey]
                    allAttributeValues = seenAttributeValues[attributeKey]
                    xmlEntry.attributes[attributeKey] = str(allAttributeValues.index(attributeValue))
        
        return None

        
    '''
        Returns the modified object for further process
        @return: a minidom XML object containing the modified data
    '''        
    def getOutput(self):
        return self.xmlObject
            
        
        




'''
    Main routine fired upon commandline execution of the program. Processes the parameters
    and calls the core functions
'''
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'USAGE: %s JUDGMENTS_INPUT.pcml.xml JUDGMENTS_OUTPUΤ.pcml.xml ' % sys.argv[0]
    else:
        
        inputXML = JudgedSet(sys.argv[1],sys.argv[2])
        inputXML.addFeatures()
        inputXML.flush()

        #path = sys.argv[2]
        #create_evaluation(input, path)