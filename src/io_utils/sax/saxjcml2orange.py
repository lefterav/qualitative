#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 21, 2011

@author: jogin, lefterav
'''

import codecs
import os
import sys
import tempfile
import shutil
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io_utils.input.xmlreader import XmlReader


class SaxJcml2Orange():
    """
    This class converts jcml format to tab format (orange format).
    The output file is saved to the same folder where input file is.
    """
    def __init__(self, input_filename, class_name, desired_attributes, meta_attributes, output_file, **kwargs):
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
        self.get_nested_attributes = False
        self.compact_mode = False
        self.discrete_attributes = []
        self.hidden_attributes = []
        self.filter_attributes = {} 
        self.class_type = "d"
        self.class_discretize = False
        self.dir = "."
        
        if "compact_mode" in kwargs:
            self.compact_mode = kwargs["compact_mode"]
        
        if "discrete_attributes" in kwargs:
            self.discrete_attributes = set(kwargs["discrete_attributes"])
        
        if "hidden_attributes" in kwargs:
            self.hidden_attributes = set(kwargs["hidden_attributes"])
        
        if "get_nested_attributes" in kwargs:
            self.get_nested_attributes = kwargs["get_nested_attributes"]
        
        if "filter_attributes" in kwargs:
            self.filter_attributes = kwargs["filter_attributes"]
            
        if "class_type" in kwargs:
            self.class_type = kwargs["class_type"]
        
        if "class_discretize" in kwargs:
            self.class_discretize = kwargs["class_discretize"]
        
        if "dir" in kwargs:
            self.dir = kwargs["dir"]
        
        self.input_filename = input_filename
        self.class_name = class_name
        self.desired_attributes = set(desired_attributes)
        self.meta_attributes = set(meta_attributes)
        
        self.orange_filename = output_file
        self.temporary_filename = tempfile.mktemp(dir=self.dir, suffix='.tab')
        #self.dataset = XmlReader(self.input_filename).get_dataset()
        self.object_file = codecs.open(self.temporary_filename, encoding='utf-8', mode = 'w')

        # get orange header
        self.get_orange_header()
        
        # get orange content
        self.get_orange_content()
        self.object_file.close()
        shutil.move(self.temporary_filename, self.orange_filename)
        print 'Orange file %s created!' % self.orange_filename
        
        # test orange file
        #self.test_orange()
        
        
    def get_orange_header(self):    
        """
        This function gets orange header.
        """
        parser = make_parser()
        curHandler1 = SaxJcmlOrangeHeader(self.object_file, self.class_name, self.desired_attributes, self.meta_attributes, self.discrete_attributes, self.get_nested_attributes, self.class_type, self.hidden_attributes, self.class_discretize)
        parser.setContentHandler(curHandler1)
        parser.parse( open(self.input_filename, 'r'))

       
    def get_orange_content(self):    
        """
        This function gets orange content.
        """
        parser = make_parser()
        curHandler2 = SaxJcmlOrangeContent(self.object_file, self.class_name, self.meta_attributes, self.compact_mode, self.filter_attributes, self.hidden_attributes, self.class_discretize)
        parser.setContentHandler(curHandler2)
        parser.parse(open(self.input_filename, 'r'))
    
    
    def test_orange(self):
        """
        Test function for getting orange file.
        """
        from io_utils.input.orangereader import OrangeData
        dataset = XmlReader(self.input_filename).get_dataset()
        wrapped_data = OrangeData(dataset, self.class_name, self.desired_attributes, self.meta_attributes, self.orange_filename)
        new_dataset = wrapped_data.get_dataset()
        

class SaxJcmlOrangeHeader(ContentHandler):
    
    
    def __init__ (self, o_file, class_name, desired_attributes, meta_attributes, discrete_attributes, get_nested_attributes, class_type, hidden_attributes=[], class_discretize = False):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of all attribute names
        @type attributeNames: list of strings
        """
        self.o_file = o_file
        self.desired_attributes = desired_attributes
        self.meta_attributes = meta_attributes
        self.discrete_attributes = discrete_attributes
        self.hidden_attributes = hidden_attributes
        self.class_name = class_name
        self.get_nested_attributes = get_nested_attributes
        self.class_type = class_type
        if class_discretize:
            self.class_type = 'd'
        
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

        self.ss_text = []
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
            self.ss_text = []
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
            self.ss_text.append(ch)
#            self.ss_text = u'%s%s' % (self.ss_text, ch)
            self.is_simple_sentence = False


    def endElement(self, name):
        self.ss_text = "".join(self.ss_text)
        if name == self.TAG_SRC:
            self.src = SimpleSentence(self.ss_text, self.ss_attributes)
            self.ss_text = []
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
        elif name == self.TAG_SENT:
            if len(self.tgt) > self.number_of_targets:
                self.number_of_targets = len(self.tgt)
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = u''
            self.tgt = []
            self.ref = u''
            if self.get_nested_attributes:
                for attribute in ps.get_nested_attributes():
                    self.attribute_names.add(str(attribute))
            else:
                for attribute in self.ps_attributes:
                    self.attribute_names.add(str(attribute))
            self.ps_attributes = {}
            
            
    def endDocument(self):
        # check if the desired attributes are in attribute names that we got from input file
        if set(self.desired_attributes) - self.attribute_names:
            notfound = set(self.desired_attributes) - self.attribute_names
            sys.stderr.write('Warning: Following desired attributes werent found in input file:\n{0}'.format(notfound))
            
        
        # first construct the lines for the declaration
        line_1 = '' # line for the name of the arguments
        line_2 = '' # line for the type of the arguments
        line_3 = '' # line for the definition of the class

        if self.desired_attributes == set([]):
            self.desired_attributes = self.attribute_names
        
        # prepare heading
        for attribute_name in self.attribute_names:
            # line 1 holds just the names
            if attribute_name in self.hidden_attributes:
                continue
            line_1 += attribute_name +"\t"
            
            #TODO: find a way to define continuous and discrete arg
            # line 2 holds the class type
            if attribute_name == self.class_name:
                line_2 += u"%s\t"% self.class_type
            elif (attribute_name in self.desired_attributes 
                  and attribute_name not in self.meta_attributes 
                  ):
                if attribute_name in self.discrete_attributes:
                    line_2 += "d\t"
                else:
                    line_2 += "c\t"
            else:
                line_2 += "s\t"

            # line 3 defines the class and the metadata
            if attribute_name == self.class_name:
                line_3 = line_3 + "c"
            elif ((attribute_name not in self.desired_attributes 
                   or attribute_name in self.meta_attributes)
                   ):
                line_3 = line_3 + "m"
            elif "id" in attribute_name:
                sys.stderr.write('One of the given features, {} seems to be a unique identifier\n'.format(attribute_name))
            
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
        
        # creating a temp file with attribute names for class SaxJcmlOrangeContent
        f = open('attribute_names.dat', 'w')
        for attribute_name in self.attribute_names:
            f.write(attribute_name + '\n') 
        f.close()


class SaxJcmlOrangeContent(ContentHandler):


    def __init__ (self, o_file, class_name, meta_attributes, compact_mode=False, filter_attributes={}, hidden_attributes=[], class_discretize=False):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of attribute names
        @type attributeNames: list of strings
        """
        self.filter_attributes = filter_attributes
        self.compact_mode = compact_mode
        self.o_file = o_file
        self.is_simple_sentence = False
        self.class_name = class_name
        self.set_tags()
        self.hidden_attributes = hidden_attributes
        self.class_discretize = class_discretize
        # reading  a temp file with attribute names for class SaxJcmlOrangeContent
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
        
        self.ss_text = []
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
            self.ss_text = []
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
            if not self.compact_mode:
#                self.ss_text = u'%s%s' % (self.ss_text, ch)
                self.ss_text.append(ch)
            self.is_simple_sentence = False


    def endElement(self, name):
        """
        Saves the data from an element that is currently ending.
        @param name: the name of the element
        @type name: string
        """
        self.ss_text = "".join(self.ss_text)
        output = []
        if name == self.TAG_SRC:
            self.src = SimpleSentence(self.ss_text, self.ss_attributes)
            self.ss_text = []
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
            self.ss_text = []
        elif name == self.TAG_SENT:
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = u''
            self.tgt = []
            self.ref = u''
            self.ps_attributes = {}
            
            #skip totally lines that have a certain value for a particular att
            for fatt in self.filter_attributes: 
                if ps.get_attribute(fatt) == self.filter_attributes[fatt]:
                    return
            
            # print source and target sentence
            for attribute_name in self.attribute_names:
                if not attribute_name in self.hidden_attributes:
                    if attribute_name == self.class_name and self.class_discretize:
                        attvalue = float(ps.get_nested_attributes()[attribute_name].strip())
                        attvalue = round(attvalue/self.class_discretize) * self.class_discretize
                        attvalue = str(attvalue)
                        output.append(u'%s\t' % attvalue)                        
                    elif attribute_name in ps.get_nested_attributes():
                        # print attribute names
                        attvalue = ps.get_nested_attributes()[attribute_name].strip()
                        attvalue.replace("inf", "99999999")
                        attvalue.replace("nan", "0")
                        output.append(u'%s\t' % attvalue)
                        
                    else:
                        # even if attribute value exists or not, we have to tab
                        output.append('0\t')
            
            # print source sentence
            output.append('%s\t' % ps.get_source().get_string())
            # print target sentences
            for tgt in ps.get_translations():
                output.append('%s\t' % tgt.get_string())
            # split parallel sentences by an additional tab and by a newline
            output.append('\t\n')
            self.o_file.write("".join(output))

#meta_attributes = set(["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", 
#                               "ps1_id", "ps2_id", "tgt-1_score" , "tgt-2_score", "tgt-1_system" , "tgt-2_system", "tgt-2_berkeley-tree", "tgt-1_berkeley-tree", "src-1_berkeley-tree", "src-2_berkeley-tree", 
#                                 ])
#SaxJcml2Orange("/home/lefterav/taraxu_data/selection-mechanism/wmt12qe/experiment/1/trainset.coupled.jcml", "rank", [], meta_attributes, "/home/lefterav/taraxu_data/selection-mechanism/wmt12qe/experiment/1/trainset.coupled.utf8.tab")