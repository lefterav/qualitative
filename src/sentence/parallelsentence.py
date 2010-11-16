#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Created on 15 Οκτ 2010

@author: elav01
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
    
    def get_feature(self, name):
        return self.features[name]
    
    def get_source(self):
        return self.src
    
    def get_translations(self):
        return self.tgt
    
    def get_reference(self):
        return self.ref
    
    def propagate_attributes(self):
        '''
            Silent function that gathers all the features of the nested sentences 
            to the parallel sentence object, by prefixing their names accordingly
        '''
        self.attributes.extend( self.__prefix__(self.src.get_attributes, "src") )
        prefixeditems = {}
        for tgtitem in self.tgt: 
             prefixeditems = self.__prefix__(self.tgtitem.get_attributes(), self.tgtitem.get_attributes()["system"] )
        self.attributes.extend( self.__prefix__(prefixeditems, "tgt") )
        for refitem in self.ref:
            self.attributes.extend( self.__prefix__(self.refitem.get_attributes, "ref") )
        
        
        
    def __prefix__(self, listitems, prefix):
        newlistitems = {}
        for item in listitems:
            item_key = prefix + "_" + item.key()
            newlistitems[item_key] = item.value
        return newlistitems  
            

        