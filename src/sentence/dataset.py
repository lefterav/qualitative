#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11 Νοε 2010

@author: elav01
'''

class DataSet(object):
    '''
    classdocs
    '''


    def __init__(self, parallelsentence_list, attributes_list):
        '''
        Constructor
        '''
        
        self.attribute_names = []
        self.attribute_names = attributes_list 
        self.parallelsentences = parallelsentence_list    
        
        #TODO: propagate up the attribute names of the nested sentences
        
    def get_parallelsentences(self):
        return self.parallelsentences
    
    def get_attribute_names(self):
        return self.attribute_names
    
    def propagate_attributes(self):

        propagated_parallelsentences = []
        for psentence in self.parallelsentences:
            propagated_parallelsentences.append( psentence.propagate )
            propagated_attribute_names = 
        self.parallelsentences = propagated_parallelsentences
    
    
        
        