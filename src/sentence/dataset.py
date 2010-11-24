#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""

class DataSet(object):
    """
    classdocs
    """

    def __init__(self, parallelsentence_list, attributes_list):
        """
        Constructor
        """
        
        self.attribute_names = []
        self.attribute_names = attributes_list 
        self.parallelsentences = parallelsentence_list    
        
        #TODO: propagate up the attribute names of the nested sentences
        
    def get_parallelsentences(self):
        return self.parallelsentences
    
    def get_attribute_names(self):
        return self.attribute_names
    
    def get_all_attribute_names(self):
        all_attribute_names = self.attribute_names
        all_attribute_names.extend( self.get_nested_attribute_names() )
        return list(set(all_attribute_names))
    
    def get_nested_attribute_names(self):
        nested_attribute_names = set()
        for parallelsentence in self.parallelsentences:
            nested_attribute_names.update ( parallelsentence.get_nested_attributes().keys() )
        return list(nested_attribute_names)
            
    
    """
     def get_nested_attributes(self):

        propagated_parallelsentences = []
        propagated_attribute_names = set()
        for psentence in self.parallelsentences:
            psentence.propagate_attributes()
            propagated_parallelsentences.append(psentence)
            propagated_attribute_names.add( psentence.get_attributes() )
        self.parallelsentences = propagated_parallelsentences
        self.attribute_names = list( propagated_attribute_names )
    """
    
        
        