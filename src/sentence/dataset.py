#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author: Eleftherios Avramidis
"""



class DataSet(object):
    """
    classdocs
    """

    def __init__(self, parallelsentence_list, attributes_list = [], annotations = []):
        """
        Constructor
        """
        
        self.parallelsentences = parallelsentence_list
        self.annotations = annotations    
        if attributes_list:
            self.attribute_names = attributes_list
            self.attribute_names_found = True
        else:
            self.attribute_names_found = False
            self.attribute_names = []

    
    def get_parallelsentences(self):
        return self.parallelsentences
    
    def get_annotations(self):
        return self.annotations
    
    def get_attribute_names(self):
        if not self.attribute_names_found: 
            self.attribute_names = self.__retrieve_attribute_names__()
            self.attribute_names_found = True
        return self.attribute_names
    
    def get_all_attribute_names(self):
        all_attribute_names =  self.get_attribute_names()
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
        return list(attribute_names)
    
    def append_dataset(self, add_dataset):
        self.parallelsentences.extend(add_dataset.get_parallelsentences())
        existing_attribute_names = set(self.get_attribute_names())
        new_attribute_names = set(add_dataset.get_attribute_names())
        merged_attribute_names = existing_attribute_names.union(new_attribute_names)
        self.attribute_names = list(merged_attribute_names)
    
    def merge_dataset(self, dataset_for_merging_with, attribute_replacements = {"rank": "predicted_rank"}, merging_attributes = ["id"]):
        """
        It takes a dataset which contains the same parallelsentences, but with different attributes.
        Incoming parallel sentences are matched with the existing parallel sentences based on the "merging attribute". 
        Incoming attributes can be renamed, so that they don't replace existing attributes.
        @param dataset_for_merging_with: the data set whose contents are to be merged with the current data set
        @type dataset_for_merging_with: DataSet
        @param attribute_replacements: listing the attribute renamings that need to take place to the incoming attributes, before the are merged
        @type attribute_replacements: list of tuples
        @param merging_attributes: the names of the attributes that signify that two parallelsentences are the same, though with possibly different attributes
        @type merging_attributes: list of strings  
        """
        incoming_parallelsentences_indexed = {}        
        incoming_parallelsentences = dataset_for_merging_with.get_parallelsentences()
        for incoming_ps in incoming_parallelsentences:
            key = "||".join([incoming_ps.get_attribute(att) for att in merging_attributes]) #hopefully this runs always in the same order
            incoming_parallelsentences_indexed[key] = incoming_ps
            
        
        for i in range(len(self.parallelsentences)):
            try:
                key = "||".join([self.parallelsentences[i].get_attribute(att) for att in merging_attributes]) #hopefully this runs always in the same order
                incoming_ps = incoming_parallelsentences_indexed[key]
                self.parallelsentences[i].merge_parallelsentence(incoming_ps, attribute_replacements)
            except:
                print "Didn't find key while merging"
                pass
            
    
    def merge_dataset_symmetrical(self, dataset_for_merging_with, attribute_replacements = {"rank": "predicted_rank"}):
        incoming_parallelsentences = dataset_for_merging_with.get_parallelsentences()
        if len(self.ps) != len(incoming_parallelsentences):
            print "error, datasets not symmetrical"
        else:
            for i in range(len(self.parallelsentences)):
                incoming_ps = incoming_parallelsentences[i]
                self.parallelsentences[i].merge_parallelsentence(incoming_ps, attribute_replacements)
               
            
            
            
    
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
            


        