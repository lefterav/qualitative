'''
Created on 14 Dec 2011

@author: elav01
'''

from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from io.dataformat.jcmlformat import JcmlFormat
import shutil
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet

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
        
        if isinstance (parallelsentences, DataSet):
            self.parallelsentences = parallelsentences.get_parallelsentences()
        else:
            self.parallelsentences = parallelsentences
        
        self.TAG = format.TAG
        
    def write_to_file(self, filename):
        '''
        XML output is written to the desired file
        '''
        tempfilename = "%s.tmp" % filename 
        file = open(tempfilename, 'w')
        generator = XMLGenerator(file, "utf-8")
        generator.startDocument()
        generator.startElement(self.TAG["doc"], {})
        for parallelsentence in self.parallelsentences:
            generator.characters("\n\t")
            generator.startElement(self.TAG["sent"], parallelsentence.get_attributes())
            
            src = parallelsentence.get_source()
            
            if isinstance(src, SimpleSentence):            
                                    
                generator._write("\n\t\t")
                generator.startElement(self.TAG["src"], src.get_attributes())
                generator.characters(src.get_string())
                generator.endElement(self.TAG["src"])
            elif isinstance(src, tuple):
                for src in parallelsentence.get_source():
                    generator._write("\n\t\t")
                    generator.startElement(self.TAG["src"], src.get_attributes())
                    generator.characters(src.get_string())
                    generator.endElement(self.TAG["src"])
            
            for tgt in parallelsentence.get_translations():
                generator._write("\n\t\t")
                generator.startElement(self.TAG["tgt"], tgt.get_attributes())
                generator.characters(tgt.get_string())
                generator.endElement(self.TAG["tgt"])
            
            
            ref = parallelsentence.get_reference()
            if ref and ref.get_string() != "":
                generator._write("\n\t\t")
                generator.startElement(self.TAG["ref"], ref.get_attributes())
                generator.characters(ref.get_string())
                generator.endElement(self.TAG["ref"])
            
            generator._write("\n\t")

            
            
            generator.endElement(self.TAG["sent"])
        generator.characters("\n")
        generator.endElement(self.TAG["doc"])
        generator.characters("\n")
        generator.endDocument()
        file.close()
        shutil.move(tempfilename, filename)
            
            
            