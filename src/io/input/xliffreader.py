#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 27, 2011

@author: jogin
'''

from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet
from xml.sax.saxutils import unescape
 

class XmlReader(object):
    """
    classdocs
    """


    def __init__(self, input_filename, load = True):
        """
        Constructor. Creates an XML object that handles basic XML data
        @param input_filename: the name of XML file 
        @type input_filename: string
        @param load: by turning this option to false, the instance will be initialized without loading everything into memory
        @type load: boolean 
        """
        self.TAG_DOC = "jcml"
        self.TAG_SENT = "judgedsentence"
        self.TAG_SRC = "src"
        self.TAG_TGT = "tgt"
        self.TAG_REF = "ref"
        self.TAG_ANNOTATIONS = "annotations"
        self.TAG_ANNOTATION = "annotation"
        self.input_filename = input_filename
        self.loaded = load
        if load:
            self.load()
    
    
    def load(self):
        """
        Loads the data of the file into memory. It is useful if the Classes has been asked not to load the filename upon initialization
        """
        self.xmlObject = parse(self.input_filename)
    
    
    def get_dataset(self):
        """
        Returs the contents of the XML file into an object structure, which is represented by the DataSet object
        Note that this will cause all the data of the XML file to be loaded into system memory at once. 
        For big data sets this may not be optimal, so consider sentence-by-sentence reading with SAX (saxjcml.py)
        @rtype: sentence.dataset.DataSet
        @return: A data set containing all the data of the XML file
        """
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
        
        
    def get_parallelsentences(self):
        """
        @return: a list of ParallelSentence objects
        """
        xmlObject = parse(self.input_filename)
        
        # get a nodeList of trans-units elements
        transUnits = xmlObject.getElementsByTagName('trans-unit')
        for transUnit in transUnits:
            # get a nodeList of alt-trans elements
            altTranss = transUnit.getElementsByTagName('alt-trans')
            
            # trans-unit source
            src = ''
            for transunit_src in transUnit.childNodes:
                if transunit_src.nodeName == 'source':
                    src = SimpleSentence(unescape(transunit_src.childNodes[0].nodeValue))

            # save attributes from desired alt-trans nodes into tgt_list
            tgt_list = []
            for altTrans in altTranss:
                # alt-trans target
                tgt = '' 
                for transunit_tgt in altTrans.childNodes:
                    if transunit_tgt.nodeName == 'target':
                        tgt = SimpleSentence(unescape(transunit_tgt.childNodes[0].nodeValue))

                # alt-trans_tool_id parsing
                tgt.add_attribute('system', altTrans.getAttribute('tool-id'))
                
                # alt-trans_score parsing 
                alttrans_scores = altTrans.getElementsByTagName("metanet:scores")
                for alttrans_score in alttrans_scores:
                    if alttrans_score in altTrans.childNodes:
                        for elem in alttrans_score.getElementsByTagName("metanet:score"):
                            tgt.add_attribute(elem.getAttribute('type'), \
                                              elem.getAttribute('value'))
                
                # alt-trans_annotation parsing
                alttrans_annotations = altTrans.getElementsByTagName("metanet:derivation")
                for alttrans_annotation in alttrans_annotations:
                    if alttrans_annotation in altTrans.childNodes:
                        for elem in alttrans_annotation.getElementsByTagName("metanet:annotation"):
                            if elem in alttrans_annotation.childNodes:
                                tgt.add_attribute(elem.getAttribute('type'), \
                                                  elem.getAttribute('value'))
                            
                # alt-trans_OOV_words
                alttrans_annotations = altTrans.getElementsByTagName("metanet:annotation")
                OOV_count = 0
                for alttrans_annotation in alttrans_annotations:
                    if alttrans_annotation.getAttribute('type') == 'oov' \
                     or alttrans_annotation.getAttribute('type') == 'OOV':
                        OOV_count += int(alttrans_annotation.getAttribute('value'))
                tgt.add_attribute('OOV_count', str(OOV_count))
                
                # add a target with new attributes to the list
                tgt_list.append(tgt)
                
            # trans-unit reference
            ref = ''
            for transunit_ref in transUnit.childNodes:
                if transunit_ref.nodeName == 'target':
                    ref = SimpleSentence(unescape(transunit_ref.childNodes[0].nodeValue))
            
            # create an object of parallel sentence
            ps = ParallelSentence(src, tgt_list, ref)
                
        xmlObject.unlink() # deallocate memory
        
        return ps

    
    def __read_attributes__(self, xmlEntry):
        """
        @return: a dictionary of the attributes of the current sentence (name:value)
        """
        attributes = {}
        attributeKeys = xmlEntry.attributes.keys()
        for attributeKey in attributeKeys:
            attributes[attributeKey] = unescape(xmlEntry.attributes[attributeKey].value)                     
        return attributes
