'''

@author: lefterav
'''
import os
import re
import codecs
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import logging

class WmtReader():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def read_parallelsentences(self, base_dir, langpair, extract_references=False):
        source_dir = "%s/plain/sources/" % base_dir
        system_outputs_dir = "%s/plain/system-outputs/" % base_dir
        reference_dir = "%s/plain/references/" % base_dir
        testsets = os.listdir(system_outputs_dir)
        
        parallelsentences = []
        
        for testset in testsets:
            source_filename ="%s/%s-src.%s" % (source_dir, testset, langpair.split("-")[0])
            reference_filename = "%s/%s-ref.%s" % (reference_dir, testset, langpair.split("-")[1])
            try:
                source_file = open(source_filename, 'r')
            except:
                logging.warn("Source file '{}' could not be opened".format(source_file))
                
            
            if extract_references:
                try:
                    reference_file = open(reference_filename, 'r')
                except:
                    logging.warn("Reference file '{}' could not be opened".format(reference_file))
                

            submissions = []           
            testset_dir = "%s/%s" % (system_outputs_dir, testset)
            langpairs = os.listdir(testset_dir)
            if not langpair in langpairs:
                print "didn't find language pair %s" % langpair
                continue
            langpair_dir =  "%s/%s" % (testset_dir, langpair)
            submission_filenames = os.listdir(langpair_dir)
            for filename in submission_filenames:
                match = re.search("\.([^.]*)$", filename)
                system_name = match.group(1)
                full_filename = "%s/%s" % (langpair_dir, filename)
                submission_file = open(full_filename, 'r')
                submissions.append((submission_file, system_name))
            
            k = 0
            for sourceline in source_file:
                translations = []
                
                for i in range(len(submissions)):
                    translation_text = submissions[i][0].readline()
                    system_name = submissions[i][1]
                    attributes = { 'system' : system_name }
                    translation = SimpleSentence(translation_text, attributes)
                    translations.append(translation)
                
                source = SimpleSentence(sourceline, {})
                attributes = {"id" : str(k+1),
                              "langsrc" : langpair.split("-")[0],
                              "langtgt" : langpair.split("-")[1],
                              "testset" : testset
                              }
                
                if extract_references:
                    referenceline = reference_file.readline();
                    reference = SimpleSentence(referenceline, {})
                else:
                    reference = None
                
                parallelsentence = ParallelSentence(source, translations, reference, attributes)
                parallelsentences.append(parallelsentence)
                k += 1
                
        return parallelsentences
                
            
if __name__ == '__main__':
    import sys
    from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
    
    langpairs = ["en-de", "de-en", "en-fr", "fr-en", "en-es", "es-en", "en-cs", "cs-en", "en-ru", "ru-en"]
    base_dir = sys.argv[1]
    output_dir = sys.argv[2]
    file_prefix = sys.argv[3]
    
    extract_references = "--ref" in sys.argv
    
    for langpair in langpairs:
        pss = WmtReader().read_parallelsentences(base_dir, langpair, extract_references)
        filename = "{}.{}.jcml".format(file_prefix, langpair)
        filename = os.path.join(output_dir, filename)
        Parallelsentence2Jcml(pss).write_to_file(filename)
    
        
        
        
