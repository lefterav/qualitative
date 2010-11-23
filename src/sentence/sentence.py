#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 28 Οκτ 2010

@author: Eleftherios Avramidis
'''

class SimpleSentence(object):
    '''
    classdocs
    '''


    def __init__(self, string="", attributes={}):
        '''
        Initializes a sentence object, which wraps both a sentence and its attributes
        '''
        
        self.string = string.replace("\t", "  ")
        self.attributes = attributes
        
    def get_string(self):
        return self.string
    
    def get_attributes(self):
        return self.attributes

    def add_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes[key]
        
        