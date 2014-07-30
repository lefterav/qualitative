'''
Created on 26 Jun 2012

@author: Eleftherios Avramidis
'''

from numpy import average, std, min, max, asarray
import logging as log
import sys

from collections import defaultdict, OrderedDict
from xml.etree.cElementTree import iterparse
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from sentence.dataset import DataSet

class CEJcmlReader():
    """
    This class converts jcml format to tab format (orange format).
    The output file is saved to the same folder where input file is.
    """
    def __init__(self, input_xml_filename, **kwargs):
        """
        Init calls class SaxJcmlOrangeHeader for creating header and 
        SaxJcmlOrangeContent for creating content.
        @param input_xml_filename: name of input jcml file
        @type input_xml_filename: string
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

        self.desired_general = kwargs.setdefault('desired_general', ["rank","langsrc","langtgt","id","judgement_id"])
        self.desired_source = kwargs.setdefault("desired_source", [])
        self.desired_target = kwargs.setdefault('desired_target', ["system","rank"])
        self.all_general = kwargs.setdefault('all_general', False)
        self.all_target = kwargs.setdefault('all_target', False)        
        self.input_filename = input_xml_filename
    
    def get_dataset(self):
        parallelsentences = []
        source_xml_file = open(self.input_filename, "r")
        # get an iterable
        context = iterparse(source_xml_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        attributes = []
        target_id = 0
        
#        desired_source = []
        targets = []
        
        
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == self.TAG_SENT:
                if not self.all_general:
                    attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if (key in self.desired_general or self.all_general)])
            #new source sentence
#            elif event == "start" and elem.tag == self.TAG_SRC:
#                source_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in desired_source])
#            
            #new target sentence
            elif event == "start" and elem.tag == self.TAG_TGT:
                target_id += 1
                target_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if (key in self.desired_target or self.all_target)])
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

    def get_parallelsentences(self, compact=True):
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
        
        src_text = ""
        tgt_text = ""
        

        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == self.TAG_SENT:
                attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in self.desired_general or self.all_general])
                targets = []
            #new source sentence
            elif event == "start" and elem.tag == self.TAG_SRC:
                source_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in self.desired_source or self.all_target])
            
            #new target sentence
            elif event == "start" and elem.tag == self.TAG_TGT:
                target_id += 1
                target_attributes = dict([(key, value) for key, value in elem.attrib.iteritems() if key in self.desired_target or self.all_target])

            elif not compact and event == "end" and elem.tag == self.TAG_SRC and elem.text:
                src_text = elem.text
                 
            elif event == "end" and elem.tag == self.TAG_TGT:
                if not compact and elem.text:
                    tgt_text = elem.text
                else:
                    tgt_text = ""
                targets.append(SimpleSentence(tgt_text, target_attributes))
            
            elif event == "end" and elem.tag in self.TAG_SENT:
                source = SimpleSentence(src_text, source_attributes)
                parallelsentence = ParallelSentence(source, targets, None, attributes)
                log.debug("cejml.py: Just process sentence {}".format(parallelsentence.get_attribute("judgement_id")))
                yield parallelsentence
            root.clear() 
        source_file.close()
        

    def fix(self, value):
        if self.remove_infinite:
            value = value.replace("inf", "9999999")
            value = value.replace("nan", "0")
        return value
           

   

def get_statistics(input_xml_filenames, **kwargs):
    vector = defaultdict(list)
    for input_xml_filename in input_xml_filenames:
        reader = CEJcmlReader(input_xml_filename, **kwargs)
        for parallelsentence in reader.get_parallelsentences(compact=True):
            general_attributes = parallelsentence.get_attributes()
            source_attributes = parallelsentence.get_source().get_attributes()
            source_attributes = dict([("src_{}".format(att), value) for att, value in source_attributes.iteritems()]) 
            try:
               ref_attributes = parallelsentence.get_reference().get_attributes()
            except:
               ref_attributes = {}
            
            general_attributes.update(source_attributes)
            general_attributes.update(ref_attributes)

            for att, value in general_attributes.iteritems():
                 vector[att].append(value)

            for target in parallelsentence.get_translations():                
                for att, value in target.get_attributes().iteritems():
                     vector["tgt_{}".format(att)].append(value)
    yield "feat \t avg \t std \t min \t max " 
    for att, values in vector.iteritems():	
        try:
            values = asarray([float(v) for v in values])
        except:
            continue
        yield "{} \t {:5.3f} \t {:5.3f} \t {:5.3f} ".format(
                                                           att,
                                                           average(values),
                                                           std(values),
                                                           min(values),
                                                           max(values)
                                                           )
            


class CEJcmlStats:
    """calculates statistics about specified attributes on an annotated JCML corpus. Low memory load"""
    
    def __init__(self, input_xml_filenames, **kwargs):
    
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'
    
        self.input_filenames = input_xml_filenames
        self.desired_general = kwargs.setdefault("desired_general", [])
        self.desired_source = kwargs.setdefault("desired_source", [])
        self.desired_target = kwargs.setdefault("desired_target", [])
        self.desired_ref = kwargs.setdefault("desired_ref", [])
        
       
    def _print_statistics(self, key, values):
        try:
            values = asarray([float(v) for v in values])
            print "{}\t{:5.3f}\t{:5.3f}\t{:5.3f}\t{:5.3f}".format(key,
                average(values),
                std(values),
                min(values),
                max(values)
            )
        except ValueError:
            print "[{}] : distinct values ".format(key)
   
    
    def get_attribute_statistics(self):
        general_attributes, source_attributes, target_attributes, ref_attributes = self.get_attribute_vectors()
        
        print "Source:"
        
        print '"{}"'.format('","'.join([key for key in source_attributes.iterkeys() if not key.endswith("_ratio") and not key.startswith("q_")]))
        
        print "\n Target:"
        
        target_attributes = OrderedDict(sorted(target_attributes.iteritems(), key=lambda t: t[0]))
        print '"{}"'.format('","'.join([key for key in target_attributes.iterkeys() if not key.endswith("_ratio") and not key.startswith("q_")]))
        
        print
        
        for key, value in general_attributes.iteritems():
            print "General attributes:\n"
            self._print_statistics(key, value)            
        
        for key, value in source_attributes.iteritems():
            print "Source attributes:\n"        
            self._print_statistics(key, value)
        
        for key, value in target_attributes.iteritems():
            print "Target attributes:\n"        
            self._print_statistics(key, value)            
            
        
    
    
    def get_attribute_vectors(self):
        """
        Extract a list of values for each attribute
        """
        general_attributes = defaultdict(list)
        source_attributes = defaultdict(list)
        target_attributes = defaultdict(list)
        ref_attributes = defaultdict(list)
        
        for input_filename in self.input_filenames:
            source_xml_file = open(input_filename, "r")
            # get an iterable
            context = iterparse(source_xml_file, events=("start", "end"))
            # turn it into an iterator
            context = iter(context)
            # get the root element
            event, root = context.next()
            
            for event, elem in context:
                #new sentence: get attributes
                if event == "start" and elem.tag == self.TAG_SENT:
                    for key, value in elem.attrib.iteritems():
    
                            general_attributes[key].append(value)
                        
                #new source sentence
                elif event == "start" and elem.tag == self.TAG_SRC:
                    for key, value in elem.attrib.iteritems():
    
                            source_attributes[key].append(value)
    
                #new target sentence
                elif event == "start" and elem.tag == self.TAG_TGT:
                    for key, value in elem.attrib.iteritems():
    
                            target_attributes[key].append(value)
                            
                elif event == "start" and elem.tag == self.TAG_REF:
                    for key, value in elem.attrib.iteritems():
    
                            ref_attributes[key].append(value)
    
                root.clear()
            
            source_xml_file.close()
        
        return general_attributes, source_attributes, target_attributes, ref_attributes
    
