#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author: Eleftherios Avramidis
"""

from copy import deepcopy

class SimpleSentence(object):
    """
    classdocs
    """


    def __init__(self, string="", attributes={}):
        """
        Initializes a simple (shallow) sentence object, which wraps both a sentence and its attributes
        @type string: string
        @param string: the string that the simple sentence will consist of
        @type attribute: {String key, String value}
        @type string: a dictionary of arguments that describe properties of the simple sentence
        
        """
        
        #avoid tabs
        self.string = string.replace("\t", "  ")
        #avoid getting a shallow reference to the attributes in the dict
        self.attributes = deepcopy (attributes) 
        
    def get_string(self):
        """
        Get the string of this simple sentence
        @rtype: String
        @return: the text contained in the simple sentence
        """
        return self.string
    
    def get_attributes(self):
        """
        Get the attributes of this sentence
        @rtype: dict
        @return: a dictionary of attributes that describe properties of the sentence
        """
        return self.attributes

    def add_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes[key]
    
    def add_attributes(self, attributes):
        self.attributes.update( attributes )
    
    def rename_attribute(self, old_name, new_name):
        self.attributes[new_name] = self.attributes[old_name]
        del(self.attributes[old_name])
        
    def del_attribute(self, attribute):
        del(self.attributes[attribute])
        
    def __str__(self):
        return self.string + ": " + str(self.attributes)
        
        