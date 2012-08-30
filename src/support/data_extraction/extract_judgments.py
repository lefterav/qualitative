'''
@author: Eleftherios Avramidis
'''

import csv
import ConfigParser
import os
import sys
import codecs
import subprocess
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.output.xmlwriter import XmlWriter

#Language mapping, needed for browsing the correct test/source/ref file
LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr',
             'Hungarian' : 'hu',
             'All': 'All'
             }

class WMTEvalReader:
    

    def __init__(self, config):
        """
        Initialize function, by providing a config file with the parameters for data and format
        @param config File object containing a config file of the required format
        """
        self.config = config
        fieldnames = config.get("format","fieldnames").split(',')
        csvfilename = "%s/%s" % (config.get("data", "path"), config.get("data", "filename"))
        csvfile = open(csvfilename, 'r')
        try:
            dialect = config.get("format","dialect")
        except:
            dialect = "excel"

        self.reader =  csv.DictReader(csvfile, fieldnames, None, None, dialect)
        self.systems_num = config.getint("format","systems_num")
        
        self.tokenize_source = False
        self.tokenize_target = False
        
        try:
            self.tokenizer = self.config.get("preprocessing", "tokenizer")
            self.tokenize_source = self.config.getboolean("preprocessing", "tokenize_source") 
            self.tokenize_target = self.config.getboolean("preprocessing", "tokenize_target")
        except:
            pass
        

       
    def parse(self):
        """
        Iterates through the csv rows, parses the data and creates a list of parallelsentences
        @return A list of Parallelsentence objects, one object for each csv row
        """ 
        parallelsentences = []
        firstrow = True
        for row in self.reader:
            
            #skip the first row as it contains headers
            if firstrow:
                firstrow = False
                continue
            
            #for some sets (eg wmt08) one needs to split a space separated cell to get some information
            if self.config.getboolean("format", "split_task_column"):
                row = self.get_task_data(row)
                
            #standardize naming of languages and testsets
            row = self.convert_languages(row)
            if not (row):
                continue
            row = self.map_testsets(row)

            #skip this row if it doesn't match filtering criteria
            if not self.check_filters(row):
                continue
            
            #additional row fields are useful for arguments of the parallel sentences but need to be renamed
            attributes = {}
            attributes = self.map_attributes(row, attributes)
            
            #this will open the file of the source sentences, get its text and create a SimpleSentence objece            
            source_text = self.extract_source(row["srclang"], row["testset"], row["srcIndex"])
            source = SimpleSentence(source_text)
            
            #this will get a list of Simplsentences containing the translations provided by the several systems from the files
            translations = self.get_translations(row)
            
            #this uses the same function for extracting source sentences, but asks for the target language id instead. this is the reference            
            reference_text = self.extract_source(row["trglang"], row["testset"], row["srcIndex"])
            reference = SimpleSentence(reference_text)
            
            #initialize object and append it to the list
            parallelsentence = ParallelSentence(source, translations, reference, attributes)
            parallelsentences.append(parallelsentence)
        
        #sort sentences with sort criteria
        for (criterion, type) in self.config.items("sort"):
            if type == "int":
                parallelsentences = sorted(parallelsentences, key=lambda parallelsentence: int(parallelsentence.get_attribute(criterion)))
            else:
                parallelsentences = sorted(parallelsentences, key=lambda parallelsentence: parallelsentence.get_attribute(criterion))
        return parallelsentences
    
    
    def map_testsets(self, row ):
        if "testset" in row:
            for (oldname, newname) in self.config.items("testsets"):
                if row["testset"].lower() == oldname:
                    row["testset"] = newname          
        else:
            row["testset"] = ""
        
        return row
            
        
    def map_attributes(self, row, attributes):
        for (attribute, key) in self.config.items("attributes"):
                try:
                    attributes[attribute] = row[key]
                except:
                    sys.stderr.write("attribute [%s:%s] failed" % (attribute, key))
                    pass
        return attributes

        
    def convert_languages(self, row):
        try:
            row["srclang"] = LANGUAGES[row["srclang"]]
            row["trglang"] = LANGUAGES[row["trglang"]]
            return row
        except:
            sys.stderr.write("Not known language\n")
            return None  
            
    def get_translations(self, row):
        
        translations = []
        system_indexing_base = self.config.getint("format","system_indexing_base")
        for i in range(system_indexing_base, self.systems_num + system_indexing_base):
            system_id = row["system%dId" % i]
            try:
                filtered_system_ids = self.config.options("filter_systems")
            except:
                filtered_system_ids = []
            if system_id and system_id not in filtered_system_ids: #avoid rows with less than n systems
                attributes = {"system": system_id, 
                          "rank": row["system%drank" % i] }
                translation_string = self.extract_translation(system_id, row["srclang"], row["trglang"], row["srcIndex"], row["testset"])
                
                translations.append(SimpleSentence(translation_string, attributes))
        return translations
    
    
    def extract_translation(self, system, srclang, trglang, sentence_index, testset):
        langpair = "%s-%s" % (srclang, trglang)
        sentence_index = int(sentence_index)
        sentence_indexing_base = self.config.getint("format","sentence_indexing_base")
        path = self.config.get("data","path")
        result = ''
        fieldmap={ 'path' : path ,
                'langpair' : langpair,
                'testset' : testset,
                'system' : system } 
                
        if system != '_ref':
            pattern_submissions = self.config.get('data', 'pattern_submissions')
            filename = pattern_submissions % fieldmap
#            try:
                #print "trying to access %s" % (pattern_submissions % fieldmap)
                
            file = open(filename, 'r')
            file = self.tokenize_file(file, trglang)
#            except:
#                sys.stderr.write("error opening %s for system %s, on language pair %s and testset %s, please filter it out through config file to proceed\n" % (filename, system, langpair, testset))
#                return ""
                #sys.exit() 
            translations = list(enumerate(file))
            for (index, sentence) in translations:
                if (index + sentence_indexing_base) == sentence_index:
                    result = sentence
                    break
                
            file.close()
        else:
            result = self.extract_source(trglang, None, sentence_index)
        
        return result

        
    
    def extract_source(self, srclang, testset, sentence_index ):
        path = self.config.get("data","path")
        sentence_index = int(sentence_index)
        sentence_indexing_base = self.config.getint("format","sentence_indexing_base")

        pattern_sourceref = self.config.get("data","pattern_sourceref")
        pattern_fields = {"path": path,
                          "srclang": srclang,
                          "testset": testset}
        full_filename = pattern_sourceref % pattern_fields
        file = open(full_filename, 'r')
        file = self.tokenize_file(file, srclang)
        translations = list(enumerate(file))
        result = ''
        for (index, sentence) in translations:
            if (index + sentence_indexing_base) == sentence_index:
                result = sentence
                break
        if result =='':
            print "Cannot resolve sentence [%d] in file %s" % (sentence_index, file.name)
        file.close()
        return result
    
    
    def tokenize_file(self, file, lang):
        if self.tokenize_target:
            try:
                return open(file.name + ".tok", 'r')
            except:     
#                file = subprocess.Popen([self.tokenizer, '-l', lang]).communicate(file)    
                file2 = open(file.name + ".tok", 'w')
                subprocess.check_call([self.tokenizer, '-l', lang], stdin=file, stdout=file2)
                file.close()
                file2.close()
                return open(file.name + ".tok", 'r')
        else:
            return file
    
    def get_system_names(self, row):
        system_names=[]
        system_indexing_base = self.config.getint("format","system_indexing_base")
        for i in range(system_indexing_base, self.systems_num + system_indexing_base):
            try:
                system_names.append(row["system%dId" % i] )
            except:
                sys.stderr.write("Could not parse system Id %d\n" % i)
        return system_names
        
            
    def get_task_data(self, row):
        task_details = row["task"].split(' ')
        row["task"] = task_details[0]
        
        #get language data
        [row["srclang"], row["trglang"]] = task_details[1].split('-')
        #get dataset
        row["testset"] = task_details[2]
        return row

    def check_filters(self, row):
        #keep that in memo
        system_names = self.get_system_names(row)
        for (field_name, value) in self.config.items("filters_include"):
            try:
                #use replacement pattern to include only rows that have required systems
                if field_name.startswith("system") and value not in system_names:
                    return False    
                #process the rest of the namely specified fields (e.g. srclang)                         
                if row[field_name] != value:
                    return False
            except:
                sys.stderr.write("skipping filter [%s]:%s, sth went wrong\n" % (field_name, value) )
                
        for (field_name, value) in self.config.items("filters_exclude"):
            try:
                if field_name.startswith("system") and value in system_names:
                    return False 

                #process the rest of the namely specified fields (e.g. srclang)                         
                if row[field_name] == value:
                    return False
            except:
                sys.stderr.write("skipping filter [%s]:%s, sth went wrong" % (field_name, value) )
    
        return True
             
             
if __name__ == "__main__":
    

    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        config = ConfigParser.RawConfigParser()
        sys.stderr.write("Opening config file: %s\n" % sys.argv[1])
        config.read([sys.argv[1]])
        wmtr = WMTEvalReader(config)
        parallelsentences = wmtr.parse()
        
        sys.stderr.write("%d sentences read, proceeding with writing XML\n" % len(parallelsentences))
        filename = config.get("output", "filename")
        Parallelsentence2Jcml(parallelsentences).write_to_file(filename)
        sys.stderr.write("Done")
        
                  
            
            
            
            
            
              
        
    
    
    
    
        
