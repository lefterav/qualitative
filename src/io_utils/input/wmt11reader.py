'''

@author: lefterav
'''
import os
import re
import codecs
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence


class Wmt11Reader():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def read_parallelsentences(self, base_dir, langpair):
        source_dir = "%s/plain/sources/" % base_dir
        system_outputs_dir = "%s/plain/system-outputs/" % base_dir
        testsets = os.listdir(system_outputs_dir)
        
        parallelsentences = []
        
        for testset in testsets:
            source_filename ="%s/%s-src.%s" % (source_dir, testset, langpair.split("-")[0])
            try:
                source_file = codecs.open(source_filename, 'r', 'utf-8')
            except:
                continue

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
                submission_file = codecs.open(full_filename, 'r', 'utf-8')
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
                parallelsentence = ParallelSentence(source, translations, None, attributes)
                parallelsentences.append(parallelsentence)
                k += 1
                
        return parallelsentences
                
            
if __name__ == '__main__':
    import sys
    from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
    import os
    
    langpairs = ["en-de", "de-en", "en-fr", "fr-en", "en-es", "es-en", "en-cs", "cs-en"]
    base_dir = sys.argv[1]
    output_dir = sys.argv[2]
    for langpair in langpairs:
        pss = Wmt11Reader().read_parallelsentences(base_dir, langpair)
        filename = "wmt12.{}.jcml".format(langpair)
        filename = os.path.join(output_dir, filename)
        Parallelsentence2Jcml(pss).write_to_file(filename)
    
        
        
        