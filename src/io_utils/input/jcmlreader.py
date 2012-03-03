#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
"""


from xml.dom.minidom import parse
from io.input.genericxmlreader import GenericXmlReader
from io.dataformat.jcmlformat import JcmlFormat

class JcmlReader(GenericXmlReader):
    """
    classdocs
    """

    
    def get_tags(self):
        TAG = JcmlFormat().get_tags()
        return TAG
        
    
    
    

    
    
   
        
    