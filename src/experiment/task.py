'''
Created on Aug 31, 2011

@author: elav01
'''

import inspect
from io.saxjcml import SaxJCMLProcessor
from xml.sax import make_parser

from io.input.jcmlreader import JcmlReader
from io.output.xmlwriter import XmlWriter

class Task(object):
    '''
    A Task represent the part of an experiment Phase, where data need to be read from one source, 
    get processed and (optionally) be written to another source. 
    The steps of the processing are defined by a list of processors (e.g. featuregenerators) to be launched sequentially
    '''
    input = ""
    output = ""
    completed = False
    file_extension = ""

    name = ""
    processors = []
    required = []
    offered = []
    
    def __init__(self, **kwargs):
        class_arguments = [member[0] for member in inspect.getmembers(self) if not member[0].startswith("__")]
        for parameter_name in kwargs:
            if parameter_name in class_arguments: 
                setattr(self, parameter_name, kwargs[parameter_name])
#        for processor in processors:
#            self.required.extend(processor.required())
#            self.offered.extend(processor.offered())


    
    def is_ready(self):
        is_ready = True
        for requirement in self.required:
            if not requirement.completed:
                is_ready = False
        return is_ready
    

    


class SerialTask(Task):
    '''
    A SerialTask is a task where each item of the data can be processed one by one, directly on the hard disk
    without having to load entire dataset into the memory. A prerequisite for this is that the given processors given 
    support processing per item (add_features_parallelsentence).  
    '''
    saxprocessor = SaxJCMLProcessor
    

    def run(self):
        self.output = self.input.replace("jcml", "%s.jcml"%self.file_extension) 
        input_file_object = open(self.input, 'r')
        output_file_object = open(self.output, 'w')
        saxreader = self.saxprocessor(output_file_object, self.processors)
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)
        input_file_object.close()
        output_file_object.close()
        self.completed = True
        #raise Exception("Unimplemented abstract method")
        

class AccumulativeTask(Task):
    '''
    An AccumulativeTask is a Task where data need to processed all in once, after being loaded into the memory.
    This can be tricky for big datasets, as memory issues may occur. Though, it is useful for running parts of 
    the experiment that do not support individual item processing (e.g. classifier training) or for processes
    that run faster when they have to do everything altogether
    '''

    reader = JcmlReader
    writer = XmlWriter   
    
    def run(self):
        self.output = self.input.replace("jcml", "%s.jcml"%self.file_extension) 
        #initialize all-in-once reader and writer
        filereader = self.reader(self.input)
        dataset = filereader.get_dataset()
        for processor in self.processors:
            dataset = processor.process_dataset(dataset)
        
        if self.output:
            filewriter = self.writer(dataset)
            filewriter.write_to_file(self.output)
        self.completed = True

class GenerativeTask(Task):
    reader = JcmlReader
    
    def run(self):
        self.output = self.input.replace("jcml", "%s.jcml"%self.file_extension) 
        filereader = self.reader(self.input)
        dataset = filereader.get_dataset()
        results = [processor.process_dataset(dataset) for processor in self.processors]
        self.completed = True
        return results
    
    