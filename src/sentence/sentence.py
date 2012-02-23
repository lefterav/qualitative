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
    
    
    def __gt__(self, other):
        return self.attributes["system"] > other.attributes["system"]
    
    def __lt__(self, other):
        return self.attributes["system"] < other.attributes["system"]
    
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

    def get_rank(self):
        return self.attributes["rank"]

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
    
    def merge_simplesentence(self, ss, attribute_replacements = {}):
        """
        Add the attributes to the object SimpleSentence().
        @param attr: attributes of a simple sentence
        @type attr: dict 
        """
        
        incoming_attributes = ss.get_attributes()
        for incoming_attribute in incoming_attributes:
            if incoming_attribute in attribute_replacements:
                new_key = attribute_replacements[incoming_attribute]
                new_value = incoming_attributes[incoming_attribute]
                incoming_attributes[new_key] = new_value
                del(incoming_attributes[incoming_attribute])     
        
        self.attributes.update(incoming_attributes)
