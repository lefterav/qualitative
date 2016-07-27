#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 27, 2011

@author: Lukas Poustka, Eleftherios Avramidis
'''


from xml.dom.minidom import parse
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from xml.sax.saxutils import unescape
from dataprocessor.input.genericreader import GenericReader
 

class RankReader(GenericReader):
    """
    Reader able to parse the ranking results from taraxu 1st evaluation round, as exported by cfedermann
    """

    def __init__(self, input_xml_filename, load = True):
        """
        Constructor. Creates an XML object that handles ranking file data
        @param input_xml_filename: the name of XML file
        @type input_xml_filename: string
        @param load: by turning this option to false, the instance will be 
                     initialized without loading everything into memory
        @type load: boolean 
        """
        self.input_filename = input_xml_filename
        self.loaded = load
        if load:
            self.load()
    
    def load(self):
        """
        Loads the data of the file into memory. It is useful if the Classes has
        been asked not to load the filename upon initialization
        """
        self.xmlObject = parse(self.input_filename)

    def unload(self):
        self.xmlObject.unlink()
        
    

    def get_parallelsentences(self):
        """
        This function parses a ranking xml file and returns a list of parallel
        sentence objects.
        @return ps_list: list of tuples in format (ranking-item_id, ParallelSentence)
        @type ps_list: list of tuples
        """
        r_items = self.xmlObject.getElementsByTagName('ranking-item')
        ps_list = []
        for r_item in r_items:
            stc_id = r_item.getAttribute('sentence_id')
            src = ''
            tgt_list = []
            
           
            for rank_child in r_item.childNodes:
                if rank_child.nodeName == 'source':
                    src = SimpleSentence(unescape(rank_child.childNodes[0].nodeValue))
                elif rank_child.nodeName != '#text':
                    tgt = SimpleSentence(unescape(rank_child.childNodes[0].nodeValue))
                    for attribute_name in rank_child.attributes.keys():
                        attribute_value = rank_child.getAttribute(attribute_name)
                        tgt.add_attribute(attribute_name, attribute_value)
                    tgt.add_attribute('system', rank_child.getAttribute('name'))
#                   tgt.add_attribute('rank', rank_child.getAttribute('rank'))
                    tgt_list.append(tgt)
            
            ps = ParallelSentence(src, tgt_list)
            #TODO: this was old, may have to change the attribute key. Commented because overlapping with other features
#            if not ps.get_attributes().has_key("id"): 
#                ps.add_attributes({'id': stc_id})
            ps.add_attributes({'sentence_id': stc_id})
            ps_list.append(ps)
        return ps_list
    
    
    
class R2RankReader(GenericReader):
    """
    Reader able to parse the ranking results from taraxu 2nd evaluation round, as exported by cfedermann
    """

    def __init__(self, input_xml_filename, load = True):
        """
        Constructor. Creates an XML object that handles ranking file data
        @param input_xml_filename: the name of XML file
        @type input_xml_filename: string
        @param load: by turning this option to false, the instance will be 
                     initialized without loading everything into memory
        @type load: boolean 
        """
        self.input_filename = input_xml_filename
        self.loaded = load
        if load:
            self.load()
    
    def load(self):
        """
        Loads the data of the file into memory. It is useful if the Classes has
        been asked not to load the filename upon initialization
        """
        self.xmlObject = parse(self.input_filename)

    def unload(self):
        self.xmlObject.unlink()
        
    

    def get_parallelsentences(self):
        """
        This function parses a ranking xml file and returns a list of parallel
        sentence objects.
        @return ps_list: list of tuples in format (ranking-item_id, ParallelSentence)
        @type ps_list: list of tuples
        """
        r_items = self.xmlObject.getElementsByTagName('ranking-item')
        ps_list = []
        for r_item in r_items:
            stc_id = r_item.getAttribute('id')
            src = SimpleSentence('')
            tgt_list = []
            
           
            for rank_child in r_item.childNodes:
                if rank_child.nodeName == 'source':
                    src = SimpleSentence(unescape(rank_child.childNodes[0].nodeValue))
                elif rank_child.nodeName == 'translation':
                    tgt = SimpleSentence('')
                    for attribute_name in rank_child.attributes.keys():
                        attribute_value = rank_child.getAttribute(attribute_name)
                        tgt.add_attribute(attribute_name, attribute_value)
#                     tgt.add_attribute('system', rank_child.getAttribute('name'))
#                   tgt.add_attribute('rank', rank_child.getAttribute('rank'))
                    tgt_list.append(tgt)
            
            attributes = {'sentence_id': stc_id,
                          'id': stc_id,  
                               'langsrc': 'de',
                               'langtgt': 'en'
                               }
            
            
            ps = ParallelSentence(src, tgt_list, None, attributes)
            #TODO: this was old, may have to change the attribute key. Commented because overlapping with other features
#            if not ps.get_attributes().has_key("id"): 
#                ps.add_attributes({'id': stc_id})
            
            ps_list.append(ps)
        return ps_list
        