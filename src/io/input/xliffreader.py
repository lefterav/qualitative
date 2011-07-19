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
 

class XliffReader(object):
    """
    classdocs
    """


    def __init__(self, input_filename, load = True):
        """
        Constructor. Creates an XML object that handles META-NET XLIFF data
        @param input_filename: the name of XML file 
        @type input_filename: string
        @param load: by turning this option to false, the instance will be 
                     initialized without loading everything into memory
        @type load: boolean 
        """
        self.input_filename = input_filename
        self.loaded = load
        if load:
            self.load()
    
    
    def load(self):
        """
        Loads the data of the file into memory. It is useful if the Classes has
        been asked not to load the filename upon initialization
        """
        self.xmlObject = parse(self.input_filename)
    
    
    def get_dataset(self):
        """
        Returs the contents of the XML file into an object structure, which is 
        represented by the DataSet object
        Note that this will cause all the data of the XML file to be loaded 
        into system memory at once. 
        For big data sets this may not be optimal, so consider 
        sentence-by-sentence reading with SAX (saxjcml.py)
        @rtype: sentence.dataset.DataSet
        @return: A data set containing all the data of the XML file
        """
        return DataSet(self.get_parallelsentences(), self.get_attributes())

    
    def length(self):
        return len(self.xmlObject.getElementsByTagName('trans-unit'))
    
    
    def get_weights(self, tool_id):
        """
        Finds the global weights for particular tool ID in file. Used by
        function get_parallelsentences().
        @tool_id: tool id
        @type string
        @return: global weights
        @type: list
        """
        weights = []
        tools = self.xmlObject.getElementsByTagName('tool')
        for tool in tools:
            if tool.getAttribute('tool-id') == tool_id:
                for elem in tool.getElementsByTagName('metanet:weight'):
                    weights.append(('%s-%s-%s' % ('global', elem.getAttribute('type'), tool_id), \
                                    elem.getAttribute('value')))
        return weights
    
    
    def get_parallelsentence(self, transUnit):
        """
        
        """ 
        
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
            tool_id = altTrans.getAttribute('tool-id')
            tgt.add_attribute('tool_id', tool_id)
            
            # add global weights for particular tool id
            for weight in self.get_weights(tool_id):
                tgt.add_attribute(weight[0], weight[1])
            
            # alt-trans_score parsing 
            alttrans_scores = altTrans.getElementsByTagName("metanet:scores")
            for alttrans_score in alttrans_scores:
                if alttrans_score in altTrans.childNodes:
                    for elem in alttrans_score.getElementsByTagName("metanet:score"):
                        tgt.add_attribute('%s-%s' % (tool_id, elem.getAttribute('type')), \
                                          elem.getAttribute('value'))
            
            # alt-trans_annotation parsing
            alttrans_annotations = altTrans.getElementsByTagName("metanet:derivation")
            for alttrans_annotation in alttrans_annotations:
                if alttrans_annotation in altTrans.childNodes:
                    for elem in alttrans_annotation.getElementsByTagName("metanet:annotation"):
                        if elem in alttrans_annotation.childNodes:
                            tgt.add_attribute('%s-%s' % (tool_id, elem.getAttribute('type')), \
                                              elem.getAttribute('value'))
                        
            # alt-trans_OOV_words
            alttrans_annotations = altTrans.getElementsByTagName("metanet:annotation")
            OOV_count = 0
            for alttrans_annotation in alttrans_annotations:
                if alttrans_annotation.getAttribute('type') == 'oov' \
                 or alttrans_annotation.getAttribute('type') == 'OOV':
                    OOV_count += int(alttrans_annotation.getAttribute('value'))
            tgt.add_attribute('%s-%s' % (tool_id, 'OOV_count'), str(OOV_count))
            
            # alt-trans token_count parsing
            token_count = {}
            for token in altTrans.getElementsByTagName('metanet:token'):
                d = token.getAttribute('id').partition('_d')[2].partition('_')[0]
                if d not in token_count:
                    token_count[d] = 1
                else:
                    token_count[d] = int(token_count[d]) + 1
            for d_count in token_count:
                tgt.add_attribute('%s-%s%s-%s' % (tool_id, 'd', d_count, \
                                      'token-count'), token_count[d_count])
            
            # add a target with new attributes to the list
            tgt_list.append(tgt)
            
        # trans-unit reference
        ref = ''
        for transunit_ref in transUnit.childNodes:
            if transunit_ref.nodeName == 'target':
                ref = SimpleSentence(unescape(transunit_ref.childNodes[0].nodeValue))
        # create an object of parallel sentence
        ps = ParallelSentence(src, tgt_list, ref)
        print "."
        return ps
    
        
    def get_parallelsentences(self):
        """
        @return: a list of ParallelSentence objects
        """
        xmlObject = self.xmlObject
        
        # get a nodeList of trans-units elements
        return [self.get_parallelsentence(transUnit) for transUnit in xmlObject.getElementsByTagName('trans-unit')]
                
        #xmlObject.unlink() # deallocate memory
        
    

    def unload(self):
        self.xmlObject.unlink()
    
    
    def __read_attributes__(self, xmlEntry):
        """
        @return: a dictionary of the attributes of the current sentence (name:value)
        """
        attributes = {}
        attributeKeys = xmlEntry.attributes.keys()
        for attributeKey in attributeKeys:
            attributes[attributeKey] = unescape(xmlEntry.attributes[attributeKey].value)                     
        return attributes
