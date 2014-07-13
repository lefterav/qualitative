'''
Created on Aug 31, 2011

@author: elav01
'''

import inspect
import sys
from io_utils.sax.saxjcml import SaxJCMLProcessor
from xml.sax import make_parser

from io_utils.input.jcmlreader import JcmlReader
from io_utils.output.xmlwriter import XmlWriter

class Task(object):
    '''
    A Task represent the part of an experiment Phase, where data need to be read from one source, 
    get processed and (optionally) be written to another source. 
    The steps of the processing are defined by a list of processors (e.g. featuregenerators) to be launched sequentially
    
    A Task is given: a dic of inputs
                     a dic of parameters
                     
    1. Each implementation of the task should specify the required input name and parameters as class attributes
    2. The Task should be initialized, by providing named arguments to the init function. Arguments that are 
        objects (i.e. classes or functions) are considered to be "inputs", whereas arguments that are constant 
        values are considered to be parameters  
                     
    '''
    
    #First define here the names of the inputs and the parameters of the particular task subclass    
    #e.g. input = None
    
    def __init__(self, **kwargs):
        '''
        The initialization of the task. Pass the named arguments provided upon the initialization of the class
        as class arguments, provided that they apply to the specific Task subclass
        '''
        argument_names = self.get_argument_names()
        for parameter_name in kwargs:
            if parameter_name in argument_names: 
                setattr(self, parameter_name, kwargs[parameter_name])        
            else:
                sys.stderr.write("Warning: Task initialization provided argument that is not specified in the particular task subclass")
                #TODO: print here the name of the subclass with the warning
    
    
    def get_argument_names(self):
        '''
        This function provides a list with the names of the arguments defined at this point for this class,
        excluding the class-specific python arguments
        '''
        argument_names = [member[0] for member in inspect.getmembers(self) if not member[0].startswith("__") and not inspect.ismethod(member[1])]
        return argument_names

    
    def get_prerequisites(self):
        '''
        It returns a list of the class arguments, if their value is another task class
        '''
        argument_names = [member[0] for member in inspect.getmembers(self) if not member[0].startswith("__") and not inspect.ismethod(member[1])]
    
    
    def get_parameters(self):
        pass
       
    
    def get_pending_prerequisites(self):
        '''
        It returns a list of task objects that need to be finished before the task of the current instance runs
        '''
        
    
    
#    input = ""
#    output = ""
#    completed = False
#    file_extension = ""
#
#    name = ""
#    processors = []
#    required = []
#    offered = []
    
#    def __init__(self, **kwargs):
#        class_arguments = [member[0] for member in inspect.getmembers(self) if not member[0].startswith("__")]
#        for parameter_name in kwargs:
#            if parameter_name in class_arguments: 
#                setattr(self, parameter_name, kwargs[parameter_name])
    
    
#        for processor in processors:
#            self.required.extend(processor.required())
#            self.offered.extend(processor.offered())


        
#    def is_ready(self):
#        is_ready = True
#        for requirement in self.required:
#            if not requirement.completed:
#                is_ready = False
#        return is_ready
    

    


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
    
    