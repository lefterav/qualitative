'''
Created on 26 Jun 2012

@author: elav01
'''

import codecs
import sys
import tempfile
import shutil
from xml.etree.cElementTree import iterparse

class SelectRank():
    """
    This class reads a JCML file and exports
     sentences with a particular rank to a text file
    """
    def __init__(self, input_filename, output_filename, desired_rank_value):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.desired_rank_value = desired_rank_value

    
    def convert(self):
        source_file = open(self.input_filename, "r")
        target_file = open(self.output_filename, 'w')
        # get an iterable
        context = iterparse(source_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        
        rank_value = None
        target_sentence = ""
        for event, elem in context:

            if event == "start" and elem.tag == self.TAG_TGT:
                rank_value = elem.attrib["rank"]
            
            elif event == "end" and elem.tag == self.TAG_TGT and float(rank_value) == float(self.desired_rank_value):
                target_sentence = elem.text
            
            elif event == "end" and elem.tag == self.TAG_SENT:
                target_file.write(target_sentence) 
                target_sentence = ""  
                rank_value = None
            
            root.clear()       
    
        target_file.close()
        source_file.close()
        
        

        