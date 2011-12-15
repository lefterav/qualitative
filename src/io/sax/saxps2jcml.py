'''
Created on 14 Dec 2011

@author: elav01
'''

from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from io.dataformat.jcmlformat import JcmlFormat


class Parallelsentence2Jcml(object):
    '''
    This is a helper function which is meant to produce quickly an XML file
    given a list of parallel sentences, without loading a new heavy XML object 
    into the memory
    '''

    def __init__(self, parallelsentences, format = JcmlFormat()):
        '''
        Provide a list of parallel sentences
        '''
        self.parallelsentences = parallelsentences
        
    def write_to_file(self, filename):
        '''
        XML output is written to the desired file
        '''
        file = open(filename, 'w')
        generator = XMLGenerator(file, "utf-8")
        generator.startDocument()
        generator.startElement("jcml", {})
        for ps in self.parallelsentences:
            generator.startElement("parallelsentence", ps.get_attributes())
        generator.endElement("jcml")
        generator.endDocument()
        file.close()
            
            
            