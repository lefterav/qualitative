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
from io.input.genericreader import GenericReader


class GenericXmlReader(GenericReader):
    """
    classdocs
    """

    
    def __init__(self, input_filename, load = True):
        """
        Constructor. Creates an XML object that handles ranking file data
        @param input_filename: the name of XML file
        @type input_filename: string
        @param load: by turning this option to false, the instance will be 
                     initialized without loading everything into memory
        @type load: boolean 
        """
        self.input_filename = input_filename
        self.loaded = load
        self.TAG = self.get_tags()
        if load:
            self.load()
            
            
    def get_tags(self):
        raise NotImplementedError( "Should have implemented this" )
 
    
    
    def load(self):
        """
        Loads the data of the file into memory. It is useful if the Classes has been asked not to load the filename upon initialization
        """
        self.xmlObject = parse(self.input_filename)
    
    
#    def get_dataset(self):
#        """
#        Returs the contents of the XML file into an object structure, which is represented by the DataSet object
#        Note that this will cause all the data of the XML file to be loaded into system memory at once. 
#        For big data sets this may not be optimal, so consider sentence-by-sentence reading with SAX (saxjcml.py)
#        @rtype: sentence.dataset.DataSet
#        @return: A data set containing all the data of the XML file
#        """
#        #return DataSet(self.get_parallelsentences(), self.get_attributes(), self.get_annotations())
#        return DataSet(self.get_parallelsentences())
    
    
#    def get_annotations(self):
#        """
#        @return a list with the names of the annotation layers that the corpus has undergone
#        """
#        try:
#            annotations_xml_container = self.xmlObject.getElementsByTagName(self.TAG["annotations"])
#            annotations_xml = annotations_xml_container[0].getElementsByTagName(self.TAG_ANNOTATION)
#            return [annotation_xml["name"] for annotation_xml in annotations_xml]
#        except:
#            print "File doesn't contain annotation information"
#            return []
#        
        

    
    
    def get_attributes(self):
        """
        @return a list of the names of the attributes contained in the XML file
        """
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG["doc"])
        sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG["sent"])
        attributesKeySet = set()
        
        for xmlEntry in sentenceList:
            for attributeKey in xmlEntry.attributes.keys():
                attributesKeySet.add(attributeKey)            
        return list(attributesKeySet)
    
    def length(self):
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG["doc"])
        return len(judgedCorpus[0].getElementsByTagName(self.TAG["sent"]))
        
    def get_parallelsentences(self, start = None, end = None):
        """
        @return: a list of ParallelSentence objects
        """
        judgedCorpus = self.xmlObject.getElementsByTagName(self.TAG["doc"])
        if not start and not end:
            sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG["sent"])
        else:
            sentenceList = judgedCorpus[0].getElementsByTagName(self.TAG["sent"])[start:end]
        newssentences = [] 
        for xmlEntry in sentenceList:
            srcXML = xmlEntry.getElementsByTagName(self.TAG["src"])
            tgtXML = xmlEntry.getElementsByTagName(self.TAG["tgt"])
            refXML = xmlEntry.getElementsByTagName(self.TAG["ref"])
            
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
            
            #TODO: fix this language by getting from other parts of the sentence
            if not self.TAG["langsrc"]  in attributes:
                attributes[self.TAG["langsrc"] ] = self.TAG["default_langsrc"] 
            
            if not self.TAG["langtgt"]  in attributes:
                attributes[self.TAG["langtgt"] ] = self.TAG["default_langtgt"] 
        
            
            #create a new Parallesentence with the given content
            curJudgedSentence = ParallelSentence(src, tgt, ref, attributes)
        
            newssentences.append(curJudgedSentence)
        return newssentences
    
    
    
    def __read_attributes__(self, xmlEntry):
        """
        @return: a dictionary of the attributes of the current sentence {name:value}
        """
        attributes = {}
        attributeKeys = xmlEntry.attributes.keys()
        for attributeKey in attributeKeys:
            attributes[attributeKey] = unescape(xmlEntry.attributes[attributeKey].value)                     
        return attributes
        
    