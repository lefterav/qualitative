#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 27, 2011

@author: jogin
'''

import string
from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet
from xml.sax.saxutils import unescape
from dataprocessor.input.genericxmlreader import GenericXmlReader

class XliffReader(GenericXmlReader):
    """
    classdocs
    """


    
    
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
        return DataSet(self.get_parallelsentences())

    
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
    
    
    def get_system_name(self, tool_id):
        """
        Finds a system name of given tool id
        @param tool_id: tool-id
        @type tool_id: string
        @return system_name: name of system
        @type system_name: string 
        """
        system_name = ''
        tools = self.xmlObject.getElementsByTagName('tool')
        for tool in tools:
            if tool.getAttribute('tool-id') == tool_id:
                system_name = tool.getAttribute('tool-name') 
                break
        return system_name
        
        
    def get_parallelsentence(self, transUnit):
        """
        
        """ 
        
        # get a nodeList of alt-trans elements
        altTranss = transUnit.getElementsByTagName('alt-trans')
        sentence_id = transUnit.getAttribute("id")
        
        # trans-unit source
        src = ''
        for transunit_src in transUnit.childNodes:
            if transunit_src.nodeName == 'source':
                src = SimpleSentence(unescape(transunit_src.childNodes[0].nodeValue))
                break

        # save attributes from desired alt-trans nodes into tgt_list
        tgt_list = []
        for altTrans in altTranss:
            # alt-trans target
            tgt = '' 
            for transunit_tgt in altTrans.childNodes:
                if transunit_tgt.nodeName == 'target':
                    tgt = SimpleSentence(unescape(transunit_tgt.childNodes[0].nodeValue))
                    break

            # alt-trans_tool_id parsing
            tool_id = altTrans.getAttribute('tool-id')
            #tgt.add_attribute('tool_id', tool_id)
            
            # system name
            #system_name = self.get_system_name(tool_id)
            #tgt.add_attribute('system', system_name)
            tgt.add_attribute('system', tool_id)
            
            # add global weights for particular tool id
            for weight in self.get_weights(tool_id):
                tgt.add_attribute(weight[0], weight[1])
            
            # alt-trans_score parsing 
            alttrans_scores = altTrans.getElementsByTagName("metanet:scores")
            for alttrans_score in alttrans_scores:
                if alttrans_score in altTrans.childNodes:
                    for elem in alttrans_score.getElementsByTagName("metanet:score"):
                        tgt.add_attribute('sc_%s-%s' % (tool_id, elem.getAttribute('type').replace(' ', '-')), \
                                          elem.getAttribute('value'))
            
            # alt-trans_annotation parsing
            alttrans_derivations = altTrans.getElementsByTagName("metanet:derivation")
            for alttrans_derivation in alttrans_derivations:
                derivation_id = alttrans_derivation.getAttribute("id")
#                tgt.add_attribute("an_%s-tokens" % derivation_id, len(alttrans_derivation.getElementsByTagName("metanet:token")))
                labels_count = {}
                if alttrans_derivation in altTrans.childNodes:
                    for elem in alttrans_derivation.getElementsByTagName("metanet:annotation"):
                        ann_type = elem.getAttribute('type').replace(' ', '-')
                        value = elem.getAttribute('value').replace("$", "SS")
                        if elem in alttrans_derivation.childNodes:
                            tgt.add_attribute('an_%s-%s-%s' % (tool_id, derivation_id, ann_type), value)
                            
                        #count node types from Lucy parser 
                        elif ann_type == "cat":
                            if labels_count.has_key(value):
                                labels_count[value] += 1
                            else:
                                labels_count[value] = 1
                #label counts collected
                for label in labels_count:
                    att_name = "%s-cat-%s" % (derivation_id, label) 
                    tgt.add_attribute(att_name, labels_count[label]) 
                            
                            
            
            
            
            
            phrases = altTrans.getElementsByTagName("metanet:phrase")
            
            if phrases:
                tgt.add_attribute("phrases_count", str(len(phrases)))
            
            phrase_id = 0
            for phrase in phrases:
                scoresets = phrase.getElementsByTagName("metanet:scores")
                phrase_id += 1
                if scoresets:
                    scoreset = scoresets[0]
                    for score in scoreset.getElementsByTagName("metanet:score"):
                        if score.getAttribute('value'):
                            value = score.getAttribute('value')
                        else:
                            value = string.strip(score.firstChild.nodeValue, "\n ")
                        tgt.add_attribute('ds_%s-%s-%d' % (tool_id, score.getAttribute('type').replace(' ', '-'), phrase_id), value)
                    
                
                
                        
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
            tokens = altTrans.getElementsByTagName('metanet:token')
            
            for token in tokens:
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
                break
        # create an object of parallel sentence
        ps = ParallelSentence(src, tgt_list, ref, {"id" : sentence_id})
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
