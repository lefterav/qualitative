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


class SaxJcmlOrangeHeader(ContentHandler):
    
    
    def __init__ (self, o_file, dataset, class_name, desired_attributes, meta_attributes):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of attribute names
        @type attributeNames: list of strings
        """
        self.o_file = o_file
        self.desired_attributes = desired_attributes
        self.meta_attributes = meta_attributes
        self.class_name = class_name
        
        self.attribute_names = set()
        
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
    
        # first construct the lines for the declaration
        line_1 = '' # line for the name of the arguments
        line_2 = '' # line for the type of the arguments
        line_3 = '' # line for the definition of the class

        
        # prepare heading
        for attribute_name in desired_attributes:
            # line 1 holds just the names
            line_1 += attribute_name +"\t"
            
            #TODO: find a way to define continuous and discrete arg
            # line 2 holds the class type
            if attribute_name == class_name:
                line_2 += "d\t"
            elif attribute_name not in meta_attributes:
                line_2 += "c\t"
            else:
                line_2 += "d\t"

            # line 3 defines the class and the metadata
            if attribute_name == class_name:
                line_3 = line_3 + "c"
            elif attribute_name in meta_attributes:
                line_3 = line_3 + "m"
            line_3 = line_3 + "\t"

        # src
        line_1 += "src\t"
        line_2 += "string\t"
        line_3 += "m\t"
        #target

        for i in range(len(dataset.get_parallelsentences()[0].get_translations())):
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
        o_file.write(output)
        

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
            self.ss_text = u""
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
            self.ss_text = u''
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
        elif name == self.TAG_SENT:
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = u''
            self.tgt = []
            self.ref = u''
            self.ps_attributes = {}
            [self.attribute_names.add(attribute) for attribute in ps.get_nested_attributes().keys()]
            
            
    def endDocument(self):
            # check if the desired attributes are in attribute names that we got from input file
            if set(self.desired_attributes) - self.attribute_names:
                print 'Following desired attributes werent found in input file:'
                print set(self.desired_attributes) - self.attribute_names, '\n'


class SaxJcml2OrangeContent(ContentHandler):


    def __init__ (self, o_file, class_name, desired_attributes, meta_attributes):
        """
        @param oFile: file object to receive processed changes
        @type oFile: file object
        @param attributeNames: a list of attribute names
        @type attributeNames: list of strings
        """
        self.o_file = o_file
        self.is_simple_sentence = False
        self.set_tags()
        self.desired_attributes = desired_attributes


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
            self.ss_text = u""
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
            self.ss_text = u''
        elif name == self.TAG_TGT:
            self.tgt.append(SimpleSentence(self.ss_text, self.ss_attributes))
            self.ss_text = u''
        elif name == self.TAG_SENT:
            ps = ParallelSentence(self.src, self.tgt, self.ref, self.ps_attributes)
            self.src = u''
            self.tgt = []
            self.ref = u''
            self.ps_attributes = {}

            # print source and target sentence
            for attribute_name in self.desired_attributes:
                if attribute_name in ps.get_nested_attributes().keys():
                    # print attribute names
                    self.o_file.write('%s\t' % ps.get_nested_attributes()[attribute_name])
            
            # print source sentence
            self.o_file.write('%s\t' % ps.get_source().get_string())
            # print target sentences
            [self.o_file.write('%s\t' % tgt.get_string()) for tgt in ps.get_translations()]
            # split parallel sentences by a newline
            self.o_file.write('\n')

class OrangeTest():
    
    def __init__ (self, dataset, class_name, desired_attributes, meta_attributes):
        import orange
        from io.input.orangereader import OrangeData 
        data = orange.ExampleTable('ojcml.tab')
        wrapped_data = OrangeData(data)
        new_dataset = wrapped_data.get_dataset() # new_dataset is a list of ps got from output file
        
        new_dataset.compare(dataset)
        print dataset == new_dataset # compare input set and output set
        
        #orangedata = OrangeData(dataset, class_name, desired_attributes, meta_attributes, True)

        #print new_dataset == orangedata.get_dataset()
        
        
    


input_filename = 'wmt08.if.partial.jcml'
output_filename = 'ojcml.tab'
desired_attributes = ['tgt-1_berkeley-avg-confidence_ratio', 'tgt-1_length_ratio', 'tgt-1_berkeley-tree', 'tgt-1_parse-NN',\
                      'tgt-1_berkeley-avg-confidence', 'tgt-2_berkeley-avg-confidence_ratio', 'tgt-2_berkeley-best-parse-confidence_ratio',\
                      'tgt-2_parse-dot', 'tgt-2_parse-VP', 'tgt-1_rank', 'tgt-2_length_ratio', 'tgt-2_parse-comma', 'tgt-1_parse-dot',\
                      'tgt-2_berkley-loglikelihood_ratio', 'tgt-2_uni-prob', 'id', 'tgt-2_parse-VB', 'tgt-1_parse-NN_ratio',\
                      'src_parse-dot', 'tgt-1_length', 'src_parse-PP', 'tgt-2_prob', 'langsrc', 'src_parse-comma',\
                      'tgt-2_parse-VP_ratio', 'tgt-1_parse-comma_ratio', 'tgt-2_orig_rank', 'src_parse-NN', 'tgt-1_orig_rank',\
                      'tgt-1_berkeley-n_ratio', 'tgt-2_parse-PP', 'tgt-1_parse-PP_ratio', 'tgt-2_parse-comma_ratio', 'tgt-1_unk',\
                      'tgt-1_parse-NP', 'tgt-2_berkeley-avg-confidence', 'tgt-1_berkeley-best-parse-confidence_ratio',\
                      'tgt-2_parse-NP_ratio', 'tgt-1_berkeley-n', 'tgt-1_tri-prob', 'tgt-1_parse-NP_ratio', 'src_length',\
                      'tgt-2_unk', 'tgt-1_berkley-loglikelihood', 'src_berkeley-best-parse-confidence', 'tgt-2_berkley-loglikelihood',\
                      'src_berkley-loglikelihood', 'tgt-1_prob', 'tgt-2_parse-dot_ratio', 'tgt-2_berkeley-best-parse-confidence',\
                      'tgt-1_uni-prob', 'judgement_id', 'tgt-2_bi-prob', 'tgt-1_bi-prob', 'tgt-1_berkeley-best-parse-confidence',\
                      'tgt-2_tri-prob', 'tgt-2_length', 'document_id', 'tgt-2_parse-NP', 'src_parse-VP', 'tgt-1_parse-PP',\
                      'src_berkeley-n', 'tgt-2_berkeley-tree', 'segment_id', 'tgt-1_parse-VP', 'tgt-1_system', 'tgt-2_parse-PP_ratio',\
                      'tgt-1_berkley-loglikelihood_ratio', 'tgt-2_berkeley-n', 'tgt-2_berkeley-n_ratio', 'src_berkeley-tree',\
                      'tgt-1_parse-VP_ratio', 'tgt-2_system', 'tgt-2_parse-NN_ratio', 'src_parse-NP', 'tgt-1_parse-dot_ratio',\
                      'src_parse-VVFIN', 'src_berkeley-avg-confidence', 'tgt-2_parse-NN', 'tgt-1_parse-comma', 'tgt-1_parse-VB',\
                      'langtgt', 'judge_id', 'src', 'tgt-1', 'tgt-2', 'ref']

meta_attributes = ['tgt-1_berkeley-avg-confidence_ratio', 'tgt-1_length_ratio', 'tgt-1_berkeley-tree', 'tgt-1_parse-NN',\
                      'tgt-1_berkeley-avg-confidence', 'tgt-2_berkeley-avg-confidence_ratio', 'tgt-2_berkeley-best-parse-confidence_ratio',\
                      'tgt-2_parse-dot', 'tgt-2_parse-VP', 'tgt-1_rank', 'tgt-2_length_ratio', 'tgt-2_parse-comma', 'tgt-1_parse-dot',\
                      'tgt-2_berkley-loglikelihood_ratio', 'tgt-2_uni-prob', 'id', 'tgt-2_parse-VB', 'tgt-1_parse-NN_ratio',\
                      'src_parse-dot', 'tgt-1_length', 'src_parse-PP', 'tgt-2_prob', 'langsrc', 'src_parse-comma',\
                      'tgt-2_parse-VP_ratio', 'tgt-1_parse-comma_ratio', 'tgt-2_orig_rank', 'src_parse-NN', 'tgt-1_orig_rank',\
                      'tgt-1_berkeley-n_ratio', 'tgt-2_parse-PP', 'tgt-1_parse-PP_ratio', 'tgt-2_parse-comma_ratio', 'tgt-1_unk',\
                      'tgt-1_parse-NP', 'tgt-2_berkeley-avg-confidence', 'tgt-1_berkeley-best-parse-confidence_ratio',\
                      'tgt-2_parse-NP_ratio', 'tgt-1_berkeley-n', 'tgt-1_tri-prob', 'tgt-1_parse-NP_ratio', 'src_length',\
                      'tgt-2_unk', 'tgt-1_berkley-loglikelihood', 'src_berkeley-best-parse-confidence', 'tgt-2_berkley-loglikelihood',\
                      'src_berkley-loglikelihood', 'tgt-1_prob', 'tgt-2_parse-dot_ratio', 'tgt-2_berkeley-best-parse-confidence',\
                      'tgt-1_uni-prob', 'judgement_id', 'tgt-2_bi-prob', 'tgt-1_bi-prob', 'tgt-1_berkeley-best-parse-confidence',\
                      'tgt-2_tri-prob', 'tgt-2_length', 'document_id', 'tgt-2_parse-NP', 'src_parse-VP', 'tgt-1_parse-PP',\
                      'src_berkeley-n', 'tgt-2_berkeley-tree', 'segment_id', 'tgt-1_parse-VP', 'tgt-1_system', 'tgt-2_parse-PP_ratio',\
                      'tgt-1_berkley-loglikelihood_ratio', 'tgt-2_berkeley-n', 'tgt-2_berkeley-n_ratio', 'src_berkeley-tree',\
                      'tgt-1_parse-VP_ratio', 'tgt-2_system', 'tgt-2_parse-NN_ratio', 'src_parse-NP', 'tgt-1_parse-dot_ratio',\
                      'src_parse-VVFIN', 'src_berkeley-avg-confidence', 'tgt-2_parse-NN', 'tgt-1_parse-comma', 'tgt-1_parse-VB',\
                      'langtgt', 'judge_id']

class_name = 'tgt-1_rank'
dataset = XmlReader(input_filename)
object_file = open(output_filename, 'w')

parser = make_parser()
curHandler1 = SaxJcmlOrangeHeader(object_file, dataset, class_name, desired_attributes, meta_attributes)
parser.setContentHandler(curHandler1)
parser.parse(open(input_filename))

parser = make_parser()
curHandler2 = SaxJcml2OrangeContent(object_file, class_name, desired_attributes, meta_attributes)
parser.setContentHandler(curHandler2)
parser.parse(open(input_filename))

OrangeTest(dataset, class_name, desired_attributes, meta_attributes)

object_file.close()
