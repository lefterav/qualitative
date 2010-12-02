#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

@author: Eleftherios Avramidis
"""

from copy import deepcopy
from sentence import SimpleSentence

class ParallelSentence(object):
    """
    classdocs
    """
    

    def __init__(self, source, translations, reference, attributes=[]):
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
    
    def get_source(self):
        return self.src
    
    def get_translations(self):
        return self.tgt
    
    def get_reference(self):
        return self.ref
    
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
            prefixeditems = self.__prefix__( tgtitem.get_attributes(), "tgt-" + str(i) )
            #prefixeditems = self.__prefix__( tgtitem.get_attributes(), tgtitem.get_attributes()["system"] )
            new_attributes.update( prefixeditems )

            new_attributes.update( self.__prefix__( self.ref.get_attributes(), "ref" ) )
        return new_attributes


    def recover_attributes(self):
        """
            Moves the attributes back to the nested sentences
            
        """
        for attribute_name in self.attributes.keys():
            attribute_value =  self.attributes[attribute_name] 
            if ( attribute_name.find('_') >0 ) :
                [tag, new_attribute_name] = attribute_name.split('_')
                if tag == 'src':                
                    self.src.add_attribute(new_attribute_name, attribute_value)
                    del self.attributes[attribute_name]
                elif tag == 'ref':
                    self.ref.add_attribute(new_attribute_name, attribute_value)
                    del self.attributes[attribute_name]
                elif tag.startswith('tgt'):
                    [tgttag, id] = tag.split('-')
                    if ( int(id)>=0 ):
                        index = int(id)-1
                        self.tgt[index].add_attribute( new_attribute_name, attribute_value)
                        del self.attributes[attribute_name]

    
        
        
    def __prefix__(self, listitems, prefix):
        newlistitems = {}
        for item_key in listitems.keys():
            new_item_key = prefix + "_" + item_key 
            newlistitems[new_item_key] = listitems[item_key]
        return newlistitems  
            

        