'''
Created on 14 Dec 2011

@author: Eleftherios Avramidis
'''

import re
import shutil
import sys
import tempfile
import logging as log
from collections import OrderedDict
from random import shuffle
import string as stringlib 
from unidecode import unidecode
from xml.sax.saxutils import XMLGenerator

from dataprocessor.dataformat.jcmlformat import JcmlFormat
from sentence.sentence import SimpleSentence
from sentence.dataset import DataSet

#compile the much needed regular expression
illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]') 
ALLOWED_PUNCTUATION = "".join(list(set(stringlib.punctuation) - set('_') - set('-')))

def c(string):
    """
    Kills extended unicode characters that are not allowed in a proper XML 
    """     
    clean_string, rep = illegal_xml_chars_RE.subn('', string)
    if rep > 0:
        sys.stderr.write("I had to kill {0} unicode characters because they were not XML-compliant\n".format(rep))
    
    return clean_string.strip()

def k(string):
    """
    Makes string suitable for XML attribute name
    """
    string = unidecode(string.decode('utf-8'))
    string = string.replace(' ', '_')
    string = string.translate(stringlib.maketrans(u"",u""), ALLOWED_PUNCTUATION)
    return string

def att(sentence):
    """
    Returns a dict for the attribute names and values including the necessary string transformation
    to avoid unicode errors
    """
    attributes = OrderedDict()
    failed = set()
    for key, val in sentence.get_attributes().iteritems():
        try:
            attributes[k(key)] = unicode(val)
        except UnicodeDecodeError:
            failed.add(k(key))
            #skip items that break the file writing, usually it's the parse tree from BitPar
            #TODO: the unicode error may originate at the importing of data from BitPar
            #attributes[k(key)] = str(val)
    if failed:
        log.debug("The following keys caused unicode errors: {}".format(list(failed)))
    return attributes


class IncrementalJcml(object):
    """
    Write line by line incrementally on an XML file, without loading anything in the memory.
    Don't forget the close function. Object sentences cannot be edited after written
    @ivar TAG: the basic tags of the XML annotation
    @type: dict((string, string))
    @ivar filename: the name of the file being written
    @type filename: string
    @ivar tempfilename: the name of the temporary file being written
    @type tempfilename: string
    @ivar generator: the python object that takes care of writing the XML
    @type generator: XMLGenerator
    """
    def __init__(self, filename, xmlformat=JcmlFormat):
        self.TAG = xmlformat.TAG
        self.filename = filename
        self.file = tempfile.NamedTemporaryFile(mode='w',delete=False,suffix='.jcml', prefix='tmp_', dir='.') #"/tmp/%s.tmp" % os.path.basename(model)
        self.tempfilename = self.file.name
        self.generator = XMLGenerator(self.file, "utf-8")
        self.generator.startDocument()
        self.generator.startElement(self.TAG["doc"], {})
        
    def add_parallelsentence(self, parallelsentence):
        """
        Write a the given parallel sentence to a JCML file. 
        @param parallelsentence: the parallel sentence to be written
        @type parallelsentences: L{sentence.parallelsentence.ParallelSentence}
        """  
        self.generator.characters("\n\t")
        #convert all attribute values to string, otherwise it breaks
        attributes = att(parallelsentence) 
        self.generator.startElement(self.TAG["sent"], attributes)
        
        src = parallelsentence.get_source()
        
        if isinstance(src, SimpleSentence):            
            self.generator.characters("\n\t\t")           
            src_attributes = att(src) 
            self.generator.startElement(self.TAG["src"], src_attributes)
            self.generator.characters(c(src.get_string()))
            self.generator.endElement(self.TAG["src"])
            
        elif isinstance(src, tuple):
            for src in parallelsentence.get_source():
                self.generator.characters("\n\t\t")
                src_attributes = att(src)
                self.generator.startElement(self.TAG["src"], src_attributes)
                self.generator.characters(c(src.get_string()))
                self.generator.endElement(self.TAG["src"])
        
        for tgt in parallelsentence.get_translations():
            self.generator.characters("\n\t\t")
            tgt_attributes = att(tgt)
            self.generator.startElement(self.TAG["tgt"], tgt_attributes)
            self.generator.characters(c(tgt.get_string()))
            self.generator.endElement(self.TAG["tgt"])
        
        ref = parallelsentence.get_reference()
        if ref and ref.get_string() != "":
            self.generator.characters("\n\t\t")
            ref_attributes = att(ref)
            self.generator.startElement(self.TAG["ref"], ref_attributes)
            self.generator.characters(c(ref.get_string()))
            self.generator.endElement(self.TAG["ref"])
        
        self.generator.characters("\n\t")
        self.generator.endElement(self.TAG["sent"])
    
    def add_parallelsentences(self, parallelsentences):
        """
        Write a the given parallel sentences to a JCML file. If the given argument is
        a generator, the parallel sentences are written incrementally in a 
        memory-efficient way
        @param parallelsentences: an iterator of parallel sentences
        @type parallelsentences: list or generator of L{sentence.parallelsentence.ParallelSentence}
        """        
        for parallelsentence in parallelsentences:
            self.add_parallelsentence(parallelsentence)
    
    def close(self):
        """
        Finalize the open entries of the XML file, flush the content and move it
        from the temporary file to the final filename 
        """
        self.generator.characters("\n")
        self.generator.endElement(self.TAG["doc"])
        self.generator.characters("\n")
        self.generator.endDocument()
        self.file.close()
        shutil.move(self.tempfilename, self.filename)
        
    def __del__(self):
        try:
            self.close()
        except:
            pass


class MultiLangpairIncrementalWriter:
    """
    Incremental JCML writer that writes the parallel sentences in a different file per
    language pair/direction. 
    @ivar writer: a dictionary that maps one incremental writer per language pair
    @type writer: IncrementalJcml
    """    
    def __init__(self, langpairs, output_pattern):
        """
        @param langpairs: a list of pairs of 2-letter language codes separated by a
        hyphen (e.g de-en)
        @type langpairs: list of strings
        @param output_pattern: a pattern compatible to the format command, that
        defines the 'langpair' field 
        @type output_pattern: string
        """
        self.writer = {}
        
        for langpair in langpairs:
            filename = output_pattern.format(langpair=langpair)
            log.info("Initializing writing sentences to {}".format(filename))
            self.writer[langpair] = IncrementalJcml(filename)
        
    
    def add_parallelsentences(self, parallelsentences):
        """
        Write a the given parallel sentences to a JCML file. If the given argument is
        a generator, the parallel sentences are written incrementally in a 
        memory-efficient way
        @param parallelsentences: an iterator of parallel sentences
        @type parallelsentences: list or generator of L{sentence.parallelsentence.ParallelSentence}
        """
        for parallelsentence in parallelsentences:
            langpair = parallelsentence.get_langpair()
            self.writer[langpair].add_parallelsentence(parallelsentence)

        
    def __del__(self):
        # close the files being written
        for writer in self.writer.values():
            writer.close()  



class Parallelsentence2Jcml(object):
    '''
    This is a helper class which is meant to produce quickly an XML file
    given a list of parallel sentences, without loading a new heavy XML object 
    into the memory
    '''

    def __init__(self, parallelsentences, format = JcmlFormat(), **kwargs):
        '''
        Provide a list of parallel sentences
        '''
        
        self.shuffle_translations = kwargs.setdefault("shuffle_translations", False)
        self.sort_attribute = kwargs.setdefault("sort_attribute", None)
                    
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
        f = open(tempfilename, 'w')
        generator = XMLGenerator(f, "utf-8")
        generator.startDocument()
        generator.startElement(self.TAG["doc"], {})

        for parallelsentence in self.parallelsentences:
            generator.characters("\n\t")
            attributes = dict([(k,unicode(v)) for k,v in parallelsentence.get_attributes().iteritems()])
            generator.startElement(self.TAG["sent"], attributes)
            
            src = parallelsentence.get_source()
            attributes = dict([(k,unicode(v)) for k,v in src.get_attributes().iteritems()])
            
            if isinstance(src, SimpleSentence):            
                                    
                generator.characters("\n\t\t")
                generator.startElement(self.TAG["src"], attributes)
                generator.characters(c(src.get_string()))
                generator.endElement(self.TAG["src"])
            elif isinstance(src, tuple):
                for src in parallelsentence.get_source():
                    generator.characters("\n\t\t")
                    generator.startElement(self.TAG["src"], attributes)
                    generator.characters(c(src.get_string()))
                    generator.endElement(self.TAG["src"])
            
            translations = parallelsentence.get_translations()
            
            if self.shuffle_translations:
                shuffle(translations)
            

            
            if self.sort_attribute:
                translations = sorted(translations, key=lambda tgt: tgt.get_attribute(self.sort_attribute))
            
            
            for tgt in translations:
                generator.characters("\n\t\t")
                attributes = dict([(k,unicode(v)) for k,v in tgt.get_attributes().iteritems()])
                generator.startElement(self.TAG["tgt"], attributes)
                generator.characters(c(tgt.get_string()))
                generator.endElement(self.TAG["tgt"])
            
            
            ref = parallelsentence.get_reference()
            if ref and ref.get_string() != "":
                generator.characters("\n\t\t")
                attributes = dict([(k,unicode(v)) for k,v in ref.get_attributes().iteritems()])
                generator.startElement(self.TAG["ref"], attributes)
                generator.characters(c(ref.get_string()))
                generator.endElement(self.TAG["ref"])
            
            generator.characters("\n\t")

            
            
            generator.endElement(self.TAG["sent"])
        generator.characters("\n")
        generator.endElement(self.TAG["doc"])
        generator.characters("\n")
        generator.endDocument()
        f.close()
        shutil.move(tempfilename, filename)
            
            
