#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""

class DataSet(object):
    """
    classdocs
    """

    def __init__(self, parallelsentence_list, attributes_list=[]):
        """
        Constructor
        """
        
        self.parallelsentences = parallelsentence_list            
        if attributes_list:
            self.attribute_names = attributes_list
        else:
            self.attribute_names = self.__retrieve_attribute_names__()
        
        
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
    
    def __retrieve_attribute_names__(self):
        attribute_names = set()
        for parallelsentence in self.parallelsentences:
            attribute_names.update( parallelsentence.get_attribute_names() )
        return attribute_names
            
            
    
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
    
    def compare(self, other_dataset, start=0, to=None ):
        """
        Compares this dataset to another, by displaying parallel sentences in pairs
        """
        if not to:
            to = len(self.parallelsentences)-1
        for ps1 in self.parallelsentences[start:to]:
            for ps2 in other_dataset.get_parallelsentences():
                if ps2.get_attributes()["id"] == ps1.get_attributes()["id"] and ps2.get_attributes()["testset"] == ps1.get_attributes()["testset"] and ps2.get_attributes()["langsrc"] == ps1.get_attributes()["langsrc"]:
                    print ps1.get_source().get_string() , "\n",  ps2.get_source().get_string()
                    print ps1.get_attributes() , "\n", ps2.get_attributes()
                    print ps1.get_translations()[0].get_string() , "\n",  ps2.get_translations()[0].get_string()
                    print ps1.get_translations()[0].get_attributes() , "\n",  ps2.get_translations()[0].get_attributes()
                    print ps1.get_translations()[1].get_string() , "\n",  ps2.get_translations()[1].get_string()
                    print ps1.get_translations()[1].get_attributes() , "\n",  ps2.get_translations()[1].get_attributes()
            
        
    
        
        