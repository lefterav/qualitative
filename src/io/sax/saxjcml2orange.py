#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 21, 2011

@author: jogin
'''

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from input.xmlreader import XmlReader
import os


class SaxJcmlOrangeHeader(ContentHandler):
    
    
    def __init__ (self, o_file, class_name, desired_attributes, meta_attributes):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of all attribute names
        @type attributeNames: list of strings
        """
        self.o_file = o_file
        self.desired_attributes = desired_attributes
        self.meta_attributes = meta_attributes
        self.class_name = class_name
        
        self.attribute_names = set()
        self.number_of_targets = 0
        
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'
        
        self.src = None
        self.tgt = []
        self.ref = None
        self.ps_list = []
        self.is_simple_sentence = False

        self.ss_text = ''
        self.ss_attributes = {}
        self.ps_attributes = {} 
        

    def startElement(self, name, attrs):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: string 
        @param attrs: of the element type as a string and the attrs parameter
        holds an object of the Attributes interface containing the attributes
        of the element.
        @type attrs: attributes
        """
        if name in [self.TAG_SRC, self.TAG_TGT]:
            self.ss_text = ''
            self.ss_attributes = {}
            for att_name in attrs.getNames():
                self.ss_attributes[att_name] = attrs.getValue(att_name)
            self.is_simple_sentence = True

        elif name == self.TAG_SENT:
            self.ps_attributes = {}
            self.tgt = []
            for att_name in attrs.getNames():
                self.ps_attributes[att_name] = attrs.getValue(att_name)


    def characters(self, ch):
        """
        The Parser will call this method to report each chunk of character data. 
        We use it to store the string of the simplesentence
        @param ch: character being parsed
        @type ch: str 
        """
        if self.is_simple_sentence:
            self.ss_text = u'%s%s' % (self.ss_text, ch)
            self.is_simple_sentence = False


    def endElement(self, name):
        if name == self.TAG_SRC:
            self.src = SimpleSentence(self.ss_text, self.ss_attributes)
            self.ss_text = ''
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
        elif name == self.TAG_SENT:
            if len(self.tgt) > self.number_of_targets:
                self.number_of_targets = len(self.tgt)
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = ''
            self.tgt = []
            self.ref = ''
            self.ps_attributes = {}
            [self.attribute_names.add(str(attribute)) for attribute in ps.get_nested_attributes().keys()]
            
            
    def endDocument(self):
        # check if the desired attributes are in attribute names that we got from input file
        if set(self.desired_attributes) - self.attribute_names:
            print 'Following desired attributes werent found in input file:'
            print set(self.desired_attributes) - self.attribute_names, '\n'
        
        # first construct the lines for the declaration
        line_1 = '' # line for the name of the arguments
        line_2 = '' # line for the type of the arguments
        line_3 = '' # line for the definition of the class

        if self.desired_attributes == []:
            self.desired_attributes = self.attribute_names
            
        # prepare heading
        for attribute_name in self.attribute_names:
            # line 1 holds just the names
            line_1 += attribute_name +"\t"
            
            #TODO: find a way to define continuous and discrete arg
            # line 2 holds the class type
            if attribute_name == class_name:
                line_2 += "d\t"
            elif attribute_name in self.desired_attributes and attribute_name not in self.meta_attributes:
                line_2 += "c\t"
            else:
                line_2 += "d\t"

            # line 3 defines the class and the metadata
            if attribute_name == class_name:
                line_3 = line_3 + "c"
            elif attribute_name not in self.desired_attributes or attribute_name in self.meta_attributes:
                line_3 = line_3 + "m"
            line_3 = line_3 + "\t"

        # src
        line_1 += "src\t"
        line_2 += "string\t"
        line_3 += "m\t"
        #target

        for i in range(self.number_of_targets):
            line_1 += "tgt-" + str(i+1) + "\t"
            line_2 += "string\t"
            line_3 += "m\t"
        #ref
        line_1 += "ref\t"
        line_2 += "string\t"
        line_3 += "m\t"
        
        #break the line in the end
        line_1 = line_1 + "\n"
        line_2 = line_2 + "\n"
        line_3 = line_3 + "\n"
        output = line_1 + line_2 + line_3
        self.o_file.write(output)
        
        # creating a temp file with attribute names for class SaxJcml2OrangeContent
        f = open('attribute_names.dat', 'w')
        [f.write(attribute_name + '\n') for attribute_name in self.attribute_names] 
        f.close()


class SaxJcml2OrangeContent(ContentHandler):


    def __init__ (self, o_file, class_name, meta_attributes):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of attribute names
        @type attributeNames: list of strings
        """
        self.o_file = o_file
        self.is_simple_sentence = False
        self.set_tags()
        # reading  a temp file with attribute names for class SaxJcml2OrangeContent
        f = open('attribute_names.dat', 'r')
        self.attribute_names = f.read().strip().split('\n')
        f.close()
        os.remove('attribute_names.dat')

    
    def set_tags(self):
        """
        Handles the basic tags used for reading the simple XML format. 
        As tags are prone to changes, this can be done by changing values here,
        or overriding accordingly
        """
        self.TAG_DOC = 'jcml'
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        
        self.src = None
        self.tgt = []
        self.ref = None
        self.ps_list = []
        
        self.ss_text = ''
        self.ss_attributes = {}
        self.ps_attributes = {}


    def startElement(self, name, attrs):
        """
        Signals the start of an element (simplesentence or parallelsentence)
        @param name: the name of the element
        @type name: string 
        @param attrs: of the element type as a string and the attrs parameter
        holds an object of the Attributes interface containing the attributes
        of the element.
        @type attrs: attributes
        """
        if name in [self.TAG_SRC, self.TAG_TGT]:
            self.ss_text = ''
            self.ss_attributes = {}
            for att_name in attrs.getNames():
                self.ss_attributes[att_name] = attrs.getValue(att_name)
            self.is_simple_sentence = True

        elif name == self.TAG_SENT:
            self.ps_attributes = {}
            self.tgt = []
            for att_name in attrs.getNames():
                self.ps_attributes[att_name] = attrs.getValue(att_name)


    def characters(self, ch):
        """
        The Parser will call this method to report each chunk of character data. 
        We use it to store the string of the simplesentence
        @param ch: character being parsed
        @type ch: str 
        """
        if self.is_simple_sentence:
            self.ss_text = u'%s%s' % (self.ss_text, ch)
            self.is_simple_sentence = False


    def endElement(self, name):
        """
        Saves the data from an element that is currently ending.
        @param name: the name of the element
        @type name: string
        """
        if name == self.TAG_SRC:
            self.src = SimpleSentence(self.ss_text, self.ss_attributes)
            self.ss_text = ''
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
            self.ss_text = ''
        elif name == self.TAG_SENT:
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = ''
            self.tgt = []
            self.ref = ''
            self.ps_attributes = {}

            # print source and target sentence
            for attribute_name in self.attribute_names:
                if attribute_name in ps.get_nested_attributes().keys():
                    # print attribute names
                    self.o_file.write('%s\t' % ps.get_nested_attributes()[attribute_name])
                else:
                    # even if attribute value exists or not, we have to tab
                    self.o_file.write('\t')
            
            # print source sentence
            self.o_file.write('%s\t' % ps.get_source().get_string())
            # print target sentences
            [self.o_file.write('%s\t' % tgt.get_string()) for tgt in ps.get_translations()]
            # split parallel sentences by an additional tab and by a newline
            self.o_file.write('\t\n')

"""
def Compare(sax, orange):
    print len(sax.split('\t')) == len(orange.split('\t'))
    print set(sax.split('\t')) == set(orange.split('\t'))
    print set(sax.split('\t')) - set(orange.split('\t'))
    print set(orange.split('\t')) - set(sax.split('\t'))

a = open('ojcml.tab', 'r')
sax = a.read()
a.close()

b = open('tmpiuZu2L.tab', 'r')
orange = b.read()
b.close()
Compare(sax, orange)

import sys
sys.exit()
"""

input_filename = 'wmt08.if.partial.jcml'
output_filename = 'ojcml.tab'
#desired_attributes = []
desired_attributes = ['tgt-1_berkeley-avg-confidence_ratio', 'tgt-1_length_ratio', 'tgt-1_berkeley-tree', 'tgt-1_parse-NN']
#meta_attributes = []
meta_attributes = ['langsrc', 'tgt-1_system', 'tgt-2_system', 'tgt-3_system', 'tgt-4_system', 'tgt-5_system', 'tgt-1_berkeley-tree',\
                   'tgt-2_berkeley-tree', 'tgt-3_berkeley-tree', 'tgt-4_berkeley-tree', 'tgt-5_berkeley-tree', 'testset',\
                   'src_berkeley-tree', 'langtgt']

class_name = 'tgt-1_rank'
dataset = XmlReader(input_filename).get_dataset()
object_file = open(output_filename, 'w')

# DESIRED METHOD OF GETTING ORANGEFILE:
# get orange header from file.xml
parser = make_parser()
curHandler1 = SaxJcmlOrangeHeader(object_file, class_name, desired_attributes, meta_attributes)
parser.setContentHandler(curHandler1)
parser.parse(open(input_filename))

# get orange content from file.xml
parser = make_parser()
curHandler2 = SaxJcml2OrangeContent(object_file, class_name, meta_attributes)
parser.setContentHandler(curHandler2)
parser.parse(open(input_filename))
object_file.close()

# TEST METHOD FOR GETTING ORANGEFILE:
import orange
from io.input.orangereader import OrangeData
wrapped_data = OrangeData(dataset, class_name, desired_attributes, meta_attributes, True)
new_dataset = wrapped_data.get_dataset()
