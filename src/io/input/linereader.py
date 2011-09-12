'''

@author: lefterav
'''
import os
import re
import codecs
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from genericreader import GenericReader

class LineReader(GenericReader):
    '''
    Reads and combines strings and attributes from one-sentence-per-line data
    '''


    def __init__(self, source_filename, submission_filenames, langpair, testset, pattern_name =""):
        '''
        Constructor
        '''
        self.source_filename = source_filename
        self.submission_filenames = submission_filenames
        self.langpair = langpair
        self.testset = testset
        self.pattern_name = pattern_name
        
    def get_parallelsentences(self):
        
        parallelsentences = []
        source_file = codecs.open(self.source_filename, 'r', 'utf-8')

        submissions = []           
        
        for filename in self.submission_filenames:
            if self.pattern_name == "":
                system_name = filename
            else:
                system_name = re.findall(self.pattern_name, filename)[0]
            submission_file = codecs.open(filename, 'r', 'utf-8')
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
                          "langsrc" : self.langpair.split("-")[0],
                          "langtgt" : self.langpair.split("-")[1],
                          "testset" : self.testset 
                          }
            parallelsentence = ParallelSentence(source, translations, None, attributes)
            parallelsentences.append(parallelsentence)
            k += 1
            
        return parallelsentences
                
            
            
        
        
        
        