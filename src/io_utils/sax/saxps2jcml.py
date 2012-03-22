'''
Created on 14 Dec 2011

@author: elav01
'''

import shutil
import sys
import re
import tempfile
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from io_utils.dataformat.jcmlformat import JcmlFormat
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet

#compile the much needed regular expression
illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]') 


def c(string):
    """
    Kills extended unicode characters that are not allowed in a proper XML 
    """    
    clean_string, rep = illegal_xml_chars_RE.subn('', string)
    if rep > 0:
        sys.stderr.write("I had to kill {0} unicode characters because they were not XML-compliant\n".format(rep))
    
    return clean_string.strip()



class IncrementalJcml(object):
    def __init__(self, filename, format = JcmlFormat()):
        self.TAG = format.TAG
        self.filename = filename
        self.file = tempfile.NamedTemporaryFile(mode='w',delete=False,suffix='.jcml', prefix='tmp_', dir='.') #"/tmp/%s.tmp" % os.path.basename(filename)
        self.tempfilename = self.file.name
#        self.file = open(self.tempfilename, 'w')
        self.generator = XMLGenerator(self.file, "utf-8")
        self.generator.startDocument()
        self.generator.startElement(self.TAG["doc"], {})
        
    def add_parallelsentence(self, parallelsentence):
        self.generator.characters("\n\t")
        self.generator.startElement(self.TAG["sent"], parallelsentence.get_attributes())
        
        src = parallelsentence.get_source()
        
        if isinstance(src, SimpleSentence):            
                                
            self.generator._write("\n\t\t")
            self.generator.startElement(self.TAG["src"], src.get_attributes())
            self.generator.characters(c(src.get_string()))
            self.generator.endElement(self.TAG["src"])
        elif isinstance(src, tuple):
            for src in parallelsentence.get_source():
                self.generator._write("\n\t\t")
                self.generator.startElement(self.TAG["src"], src.get_attributes())
                self.generator.characters(c(src.get_string()))
                self.generator.endElement(self.TAG["src"])
        
        for tgt in parallelsentence.get_translations():
            self.generator._write("\n\t\t")
            self.generator.startElement(self.TAG["tgt"], tgt.get_attributes())
            self.generator.characters(c(tgt.get_string()))
            self.generator.endElement(self.TAG["tgt"])
        
        
        ref = parallelsentence.get_reference()
        if ref and ref.get_string() != "":
            self.generator._write("\n\t\t")
            self.generator.startElement(self.TAG["ref"], ref.get_attributes())
            self.generator.characters(c(ref.get_string()))
            self.generator.endElement(self.TAG["ref"])
        
        self.generator._write("\n\t")
        self.generator.endElement(self.TAG["sent"])
        
    
    def close(self):
        self.generator.characters("\n")
        self.generator.endElement(self.TAG["doc"])
        self.generator.characters("\n")
        self.generator.endDocument()
        self.file.close()
        shutil.move(self.tempfilename, self.filename)

class Parallelsentence2Jcml(object):
    '''
    This is a helper class which is meant to produce quickly an XML file
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
                generator.characters(c(src.get_string()))
                generator.endElement(self.TAG["src"])
            elif isinstance(src, tuple):
                for src in parallelsentence.get_source():
                    generator._write("\n\t\t")
                    generator.startElement(self.TAG["src"], src.get_attributes())
                    generator.characters(c(src.get_string()))
                    generator.endElement(self.TAG["src"])
            
            for tgt in parallelsentence.get_translations():
                generator._write("\n\t\t")
                generator.startElement(self.TAG["tgt"], tgt.get_attributes())
                generator.characters(c(tgt.get_string()))
                generator.endElement(self.TAG["tgt"])
            
            
            ref = parallelsentence.get_reference()
            if ref and ref.get_string() != "":
                generator._write("\n\t\t")
                generator.startElement(self.TAG["ref"], ref.get_attributes())
                generator.characters(c(ref.get_string()))
                generator.endElement(self.TAG["ref"])
            
            generator._write("\n\t")

            
            
            generator.endElement(self.TAG["sent"])
        generator.characters("\n")
        generator.endElement(self.TAG["doc"])
        generator.characters("\n")
        generator.endDocument()
        file.close()
        shutil.move(tempfilename, filename)
            
            
            