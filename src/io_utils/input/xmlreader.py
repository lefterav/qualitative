#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Created on 15 Οκτ 2010

@author: Eleftherios Avramidis
"""



from io_utils.input.genericxmlreader import GenericXmlReader
from io_utils.dataformat.jcmlformat import JcmlFormat

class XmlReader(GenericXmlReader):
    """
    classdocs
    """

    
    def get_tags(self):
        TAG = JcmlFormat().get_tags()
        return TAG
        
    
    
    

    
    
   
        
    