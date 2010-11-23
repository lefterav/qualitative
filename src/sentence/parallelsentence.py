#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
'''

class ParallelSentence(object):
    '''
    classdocs
    '''
    

    def __init__(self, source, translations, reference, attributes):
        '''
        Constructor
        @param source The source text of the parallel sentence
        @param translations A list of given translations 
        @param reference The desired translation provided by the system
        '''
        self.src = source
        self.tgt = translations
        self.ref = reference
        self.attributes = attributes
    
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
        '''
            function that gathers all the features of the nested sentences 
            to the parallel sentence object, by prefixing their names accordingly
        '''
        new_attributes = self.attributes
        new_attributes.update( self.__prefix__(self.src.get_attributes(), "src") )
        i=0
        for tgtitem in self.tgt:
            i += 1
            prefixeditems = self.__prefix__( tgtitem.get_attributes(), "tgt" + str(i) )
            #prefixeditems = self.__prefix__( tgtitem.get_attributes(), tgtitem.get_attributes()["system"] )
            new_attributes.update( prefixeditems )

        for refitem in self.ref:
            new_attributes.update( self.__prefix__( refitem.get_attributes, "ref" ) )
        return new_attributes

    
        
        
    def __prefix__(self, listitems, prefix):
        newlistitems = {}
        for item_key in listitems.keys():
            new_item_key = prefix + "_" + item_key 
            newlistitems[new_item_key] = listitems[item_key]
        return newlistitems  
            

        