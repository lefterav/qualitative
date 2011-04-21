#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

@author: Eleftherios Avramidis
"""

from copy import deepcopy
from sentence import SimpleSentence
import sys
import re

class ParallelSentence(object):
    """
    classdocs
    """
    

    def __init__(self, source, translations, reference=None, attributes={}):
        """
        Constructor
        @type source SimpleSentence
        @param source The source text of the parallel sentence
        @type translations list ( SimpleSentence )
        @param translations A list of given translations
        @type reference SimpleSentence 
        @param reference The desired translation provided by the system
        @type attributes dict { String name , String value }
        @param the attributes that describe the parallel sentence
        """
        self.src = source
        self.tgt = translations
        self.ref = reference
        self.attributes = deepcopy (attributes)
    
    def get_attributes (self):
        return self.attributes
    
    def get_attribute_names (self):
        return self.attributes.keys()
    
    def get_attribute(self, name):
        return self.attributes[name]
    
    def add_attributes (self, attributes):
        self.attributes.update( attributes )
    
    def set_langsrc (self, langsrc):
        self.attributes["langsrc"] = langsrc

    def set_langtgt (self, langtgt):
        self.attributes["langtgt"] = langtgt
        
    def set_id (self, id):
        self.attributes["id"] = str(id)
    
    def get_source(self):
        return self.src
    
    def set_source(self,src):
        self.src = src
    
    def get_translations(self):
        return self.tgt
    
    def set_translations(self, tgt):
        self.tgt = tgt
    
    def get_reference(self):
        return self.ref
    
    def set_reference(self,ref):
        self.ref = ref
    
    def get_nested_attributes(self):
        """
        function that gathers all the features of the nested sentences 
        to the parallel sentence object, by prefixing their names accordingly
        """
        
        new_attributes = deepcopy (self.attributes)
        new_attributes.update( self.__prefix__(self.src.get_attributes(), "src") )
        i=0
        for tgtitem in self.tgt:
            i += 1
            prefixeditems = self.__prefix__( tgtitem.get_attributes(), "tgt-%d" % i )
            #prefixeditems = self.__prefix__( tgtitem.get_attributes(), tgtitem.get_attributes()["system"] )
            new_attributes.update( prefixeditems )

            try:
                new_attributes.update( self.__prefix__( self.ref.get_attributes(), "ref" ) )
            except:
                pass
        return new_attributes


    def recover_attributes(self):
        """
        Moves the attributes back to the nested sentences
            
        """
        
        for attribute_name in self.attributes.keys():
            attribute_value =  self.attributes[attribute_name] 
            if (attribute_name.find('_') > 0) :

                src_attribute = re.match("src_(.*)", attribute_name)
                if src_attribute:
                    self.src.add_attribute(src_attribute.group(1), attribute_value)
                    del self.attributes[attribute_name]
                
                ref_attribute = re.match("ref_(.*)", attribute_name)
                if ref_attribute:
                    self.src.add_attribute(ref_attribute.group(1), attribute_value)
                    del self.attributes[attribute_name]
                
                tgt_attribute = re.match("tgt-([0-9]*)_(.*)", attribute_name)
                if tgt_attribute:
                    index = int(tgt_attribute.group(1)) - 1
                    new_attribute_name = tgt_attribute.group(2)
                    self.tgt[index].add_attribute(new_attribute_name, attribute_value)
                    del self.attributes[attribute_name]

    
    def serialize(self):
        list = []
        list.append(self.src)
        list.extend(self.tgt)
        return list
        
        
    def __prefix__(self, listitems, prefix):
        newlistitems = {}
        for item_key in listitems.keys():
            new_item_key = "_".join([prefix, item_key]) 
            newlistitems[new_item_key] = listitems[item_key]
        return newlistitems              
