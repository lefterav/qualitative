'''
Created on 26 Jun 2012

@author: elav01
'''

import codecs
import sys
import tempfile
import shutil
from xml.etree.cElementTree import iterparse
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet

class CEJcmlReader():
    """
    This class converts jcml format to tab format (orange format).
    The output file is saved to the same folder where input file is.
    """
    def __init__(self, input_filename, **kwargs):
        """
        Init calls class SaxJcmlOrangeHeader for creating header and 
        SaxJcmlOrangeContent for creating content.
        @param input_filename: name of input jcml file
        @type input_filename: string
        @param class_name: name of class
        @type class_name: string
        @param desired_attributes: desired attributes
        @type desired_attributes: list of strings
        @param meta_attributes: meta attributes
        @type meta_attributes: list of strings
         
        """

        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'

        self.desired_general = kwargs.setdefault('desired_general', ["rank","langsrc","langtgt","id"])
        self.desired_target = kwargs.setdefault('desired_target', ["system"])
        self.input_filename = input_filename
    
    def get_dataset(self):
        parallelsentences = []
        source_file = open(self.input_filename, "r")
        # get an iterable
        context = iterparse(source_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        attributes = []
        target_id = 0
        
#        desired_source = []

        
        
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == self.TAG_SENT:
                attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in self.desired_general])
                targets = []
            #new source sentence
#            elif event == "start" and elem.tag == self.TAG_SRC:
#                source_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in desired_source])
#            
            #new target sentence
            elif event == "start" and elem.tag == self.TAG_TGT:
                target_id += 1
                target_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in self.desired_target])
                targets.append(SimpleSentence("", target_attributes))
            
#            elif event == "end" and elem.tag == self.TAG_SRC:
#                src_text = elem.text
            
#            elif event == "end" and elem.tag == self.TAG_TGT:
#                tgt_text.append(elem.text)
            
            elif event == "end" and elem.tag in self.TAG_SENT:
                source = SimpleSentence("",{})
                parallelsentence = ParallelSentence(source,targets,None,attributes)
                parallelsentences.append(parallelsentence)
            root.clear()
        
        
        return DataSet(parallelsentences)       
    
    
