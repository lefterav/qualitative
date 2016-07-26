#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
"""


from xml.dom.minidom import parse
from dataprocessor.input.genericxmlreader import GenericXmlReader
from dataprocessor.dataformat.jcmlformat import JcmlFormat

class JcmlReader(GenericXmlReader):
    """
    classdocs
    """

    
    def get_tags(self):
        TAG = JcmlFormat().get_tags()
        return TAG
        
    
    
    

    
    
   
        
    