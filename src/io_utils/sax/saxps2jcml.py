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



def c(string):
    """
    Kills extended unicode characters that are not allowed in a proper XML 
    """
    ranges = [(0, 8), (0xb, 0x1f), (0x7f, 0x84), (0x86, 0x9f), (0xd800, 0xdfff), (0xfdd0, 0xfddf), (0xfffe, 0xffff)]
    # fromkeys creates  the wanted (codepoint -> None) mapping
    nukemap = dict.fromkeys(r for start, end in ranges for r in range(start, end+1))
    clean = dirty.translate(nukemap)
    
    
    illegal_unichrs = [ (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
                (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
                (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
                (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
                (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
                (0x10FFFE, 0x10FFFF) ]

    illegal_ranges = ["%s-%s" % (unichr(low), unichr(high)) 
                      for (low, high) in illegal_unichrs 
                      if low < sys.maxunicode]
    
    illegal_xml_re = re.compile(u'[%s]' % u''.join(illegal_ranges))
    clean_string, rep = illegal_xml_re.subn('', string)
    if rep > 0:
        sys.stderr.write("I had to kill {0} unicode characters because they were not XML-compliant\n".format(rep))
    return clean_string 



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
            
            
            