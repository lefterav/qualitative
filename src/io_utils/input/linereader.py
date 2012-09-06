'''

@author: Eleftherios Avramidis
'''
import re
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from genericreader import GenericReader

class LineReader(GenericReader):
    '''
    Reads and combines strings from one-sentence-per-line data
    '''


    def __init__(self, source_filename, submission_filenames, langpair, testset, pattern_name =""):
        '''
        @param source_filename: Name of file containing source sentences, one sentence per line
        @type source_filename: str
        @param submission_filenames: List of files containing MT system output corresponding with 
        the source file, one sentence per line. The filename of each file will be used for extracting
        the 'system' attribute for its imported sentences (see \L{pattern_name} below)
        @type submission_filenames: str
        @param langpair: A string containing the language codes of the the language pair, source-target e.g.: de-en or en-fr
        @type langpair: str
        @param testset: The name of the data set, e.g: testset2011
        @type testset: str
        @param pattern_name: A regular expression which contains a bracketed pattern for extracting 
        the system name out of the filename. If empty, the entire filename will be used as a system name 
        '''
        self.source_filename = source_filename
        self.submission_filenames = submission_filenames
        self.langpair = langpair
        self.testset = testset
        self.pattern_name = pattern_name
        
        
    def get_parallelsentences(self):
        parallelsentences = []
        source_file = open(self.source_filename, 'r')

        submissions = []           
        
        for filename in self.submission_filenames:
            if self.pattern_name == "":
                system_name = filename
            else:
                system_name = re.findall(self.pattern_name, filename)[0]
            submission_file = open(filename, 'r')
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
                

class AttributeLineReader(GenericReader):
    '''
    Reads and combines strings and attributes from one-sentence-per-line data
    '''

    def __init__(self):
        pass
        
    
    def get_parallelsentences(self):
        parallelsentences = []
        source_file = open(self.source_filename, 'r')

        submissions = []           
        
        for filename in self.submission_filenames:
            if self.pattern_name == "":
                system_name = filename
            else:
                system_name = re.findall(self.pattern_name, filename)[0]
            submission_file = open(filename, 'r')
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
        
        