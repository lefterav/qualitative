'''
Convert from the QTleap CSV format to jcml
Created on 7 Mar 2016

@author: elav01
'''

from dataprocessor.datareader import DataReader
from csv import DictReader
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from collections import defaultdict

class QtleapCSVReader(DataReader):
    
    def __init__(self, model, sourcefile=None, 
                 source_language="en", target_language="de"):
        self.filename = model
        self.source_language = source_language
        self.target_language = target_language
        self.indexed_sources = defaultdict(str)
        i = 0
        if sourcefile:
            sourcefile_object = open(sourcefile)
            for line in sourcefile_object:
                i+=1
                self.indexed_sources[i] = line.strip()
                
    def get_parallelsentences(self):
        with open(self.filename, 'rb') as csvfile:
            translations = []
            csvreader = DictReader(csvfile, delimiter=',', quotechar='"')
            previous_segment_id = None
            reference_string = ""
            
            for row in csvreader:
                segment_id = int(row['idQuestion'])
                #if a new id comes, then emit the previously formed parallel sentence
                if segment_id != previous_segment_id and previous_segment_id != None:
                    
                    yield ParallelSentence(SimpleSentence(self.indexed_sources[previous_segment_id]),
                                           translations,
                                           SimpleSentence(reference_string),
                                           langsrc=self.source_language,
                                           langtgt=self.target_language,
                                           segment_id=previous_segment_id
                                           )
                    translations = []
                previous_segment_id = segment_id
                
                #form the attributes for the simple sentence
                translation_string = row['answer_de']
                attributes = {"system" : "pilot_{}".format(row['Pilot']),
                              "rank" : row['rank'],
                              "judge_id" : row['user']}
                
                translation = SimpleSentence(translation_string, attributes)
                #and added in the list of this parallel sentence
                translations.append(translation)

                reference_string = row['manual_answer']
                
            #emit the last parallelsentence
            yield ParallelSentence(SimpleSentence(self.indexed_sources[segment_id]),
                             translations, 
                             SimpleSentence(reference_string),
                             langsrc=self.source_language,
                             langtgt=self.target_language,
                             segment_id=previous_segment_id
                             )    
    