'''
Created on 26 Jun 2012

@author: elav01
'''

import codecs
import sys
import tempfile
import shutil
from xml.etree.cElementTree import iterparse

class CElementTreeJcml2Orange():
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
        
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'
        
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
        self.attribute_names, self.number_of_targets = self._get_attribute_names()
        self.object_file.write(self._get_header_text())
        
        
    def _get_attribute_names(self):
        '''
        Parse once the given XML file and return a set with the attribute names
        @param input_filename: The XML file to be parsed
        '''
        source_file = open(self.input_filename, "r")
        # get an iterable
        context = iterparse(source_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()

        number_of_targets = 0
        attribute_names = []
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == self.TAG_SENT:
                attribute_names.extend(elem.attrib.keys())   
                target_id = 0         
            #new source sentence
            elif event == "start" and elem.tag == self.TAG_SRC:
                source_attributes = ["src_{}".format(key) for key in elem.attrib.keys()]
                attribute_names.extend(source_attributes)
            #new target sentence
            elif event == "start" and elem.tag == self.TAG_TGT:
                target_id += 1
                target_attributes = ["tgt-{0}_{1}".format(target_id, key) for key in elem.attrib.keys()]
                attribute_names.extend(target_attributes)
            elif event == "end" and elem.tag == self.TAG_SENT:
                if target_id > number_of_targets:
                    number_of_targets = target_id
            root.clear()
        source_file.close()
        return set(attribute_names), number_of_targets
    
    
    def _get_header_text(self):
        # check if the desired attributes are in attribute names that we got from input file
        if set(self.desired_attributes) - self.attribute_names:
            notfound = set(self.desired_attributes) - self.attribute_names
            sys.stderr.write('Warning: Following desired attributes werent found in input file:\n{0}'.format(notfound))
            
        
        # first construct the lines for the declaration
        line_1 = [] # line for the name of the arguments
        line_2 = [] # line for the type of the arguments
        line_3 = [] # line for the definition of the class

        if self.desired_attributes == set([]):
            self.desired_attributes = self.attribute_names - self.meta_attributes
        
        # prepare heading
        for attribute_name in self.attribute_names:
            # line 1 holds just the names
            
            #skip hidden attributes
            if attribute_name in self.hidden_attributes:
                continue
            line_1.append(attribute_name)
            
            #TODO: find a way to define continuous and discrete arg
            # line 2 holds the class type
            if attribute_name == self.class_name:
                line_2.append(self.class_type)
            elif (attribute_name in self.desired_attributes 
                  and attribute_name not in self.meta_attributes 
                  ):
                if attribute_name in self.discrete_attributes:
                    line_2.append("d")
                else:
                    line_2.append("c")
            else:
                line_2.append("s")

            # line 3 defines the class and the metadata
            if attribute_name == self.class_name:
                line_3.append("c")
            elif ((attribute_name not in self.desired_attributes 
                   or attribute_name in self.meta_attributes)
                   ):
                line_3.append("m")
            elif "id" == attribute_name or "_id" in attribute_name or "-id" in attribute_name or ".id" in attribute_name:
                sys.stderr.write('Warning: One of the given features, {} seems to be a unique identifier\n'.format(attribute_name))
                line_3.append("")
            else:
                line_3.append("")

        # src
        line_1.append("src")
        line_2.append("string")
        line_3.append("m")
        #target

        for i in range(self.number_of_targets):
            line_1.append("tgt-{0}".format(i+1))
            line_2.append("string")
            line_3.append("m")
        #ref
#        line_1 += "ref\t"
#        line_2 += "string\t"
#        line_3 += "m\t"
        
        line_1 = "\t".join(line_1)
        line_2 = "\t".join(line_2)
        line_3 = "\t".join(line_3)
        #break the line in the end
        line_3 = line_3 + "\n"
        
        output = "\n".join([line_1, line_2, line_3])
        return output


    def get_orange_content(self):
        
        source_file = open(self.input_filename, "r")
        # get an iterable
        context = iterparse(source_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        attributes = []
        target_id = 0
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == self.TAG_SENT:
                attributes = elem.attrib
                tgt_text = [] 
                attribute_list = []
                target_id = 0
            #new source sentence
            elif event == "start" and elem.tag == self.TAG_SRC:
                source_attributes = [("src_{}".format(key), value) for key, value in elem.attrib.iteritems()]
                attribute_list.extend(source_attributes)
            
            #new target sentence
            elif event == "start" and elem.tag == self.TAG_TGT:
                target_id += 1
                target_attributes = [("tgt-{0}_{1}".format(target_id, key), value) for key, value in elem.attrib.iteritems()]
                attribute_list.extend(target_attributes)
            
            elif event == "end" and elem.tag == self.TAG_SRC:
                src_text = elem.text
            
            elif event == "end" and elem.tag == self.TAG_TGT:
                tgt_text.append(elem.text)
            
            elif event == "end" and elem.tag in self.TAG_SENT:
                attributes.update(dict(attribute_list))
                self._write_orange_line(attributes, src_text, tgt_text)
                
            root.clear()       
    
    
    
    def _write_orange_line(self, ps_nested_attributes, src_text, tgt_text):
        #skip totally lines that have a certain value for a particular att
        for fatt in self.filter_attributes: 
            if ps_nested_attributes[fatt] == self.filter_attributes[fatt]:
                return
        
        output = []
        # print source and target sentence
        for attribute_name in self.attribute_names:
            if not attribute_name in self.hidden_attributes:
                if attribute_name == self.class_name and self.class_discretize:
                    attvalue = float(ps_nested_attributes[attribute_name].strip())
                    attvalue = round(attvalue/self.class_discretize) * self.class_discretize
                    attvalue = str(attvalue)
                    output.append(attvalue)     
                    output.append("\t")                  
                elif attribute_name in ps_nested_attributes:
                    # print attribute names
                    attvalue = ps_nested_attributes[attribute_name].strip()
                    attvalue.replace("inf", "99999999")
                    attvalue.replace("nan", "0")
                    output.append(attvalue)
                    output.append("\t")
                    
                else:
                    # even if attribute value exists or not, we have to tab
                    output.append('\t')
        
        # print source sentence
        output.append(src_text)
        output.append("\t")
        # print target sentences
        for tgt in tgt_text:
            output.append(tgt)
            output.append('\t')
        # split parallel sentences by an additional tab and by a newline
        output.append('\n')
        line =  "".join(output)
        self.object_file.write(line)
        
        
        
        

        