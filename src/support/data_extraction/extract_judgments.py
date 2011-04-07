import csv
import ConfigParser
import os
import sys
import codecs
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io.output.xmlwriter import XmlWriter


#Language mapping, needed for browsing the correct test/source/ref file
LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr',
             'Hungarian' : 'hu'
             }

class WMTEvalReader:
    

    def __init__(self, config):
        self.config = config
        fieldnames = config.get("format","fieldnames").split(',')
        csvfilename = "%s/%s" % (config.get("data", "path"), config.get("data", "filename"))
        csvfile = open(csvfilename)
        self.reader =  csv.DictReader(csvfile, fieldnames)
        self.systems_num = config.getint("format","systems_num")
        
    def parse(self):
        parallelsentences = []
        firstrow = True
        for row in self.reader:
            
            if firstrow:
                firstrow = False
                continue
            
            attributes = {}
            
            if self.config.getboolean("format", "split_task_column"):
                row = self.get_task_data(row)
                
            row = self.convert_languages(row)
                   
            if "testset" in row:
                attributes["testset"] = row["testset"]
            else:
                row["testset"] = ""

            #skip this row if it doesn't match filtering criteria
            if not self.check_filters(row):
                continue
            
            attributes["id"] = row["srcIndex"]
            attributes["document_id"] = row["documentId"]
            attributes["segment_id"] = row["segmentId"]
            attributes["judge_id"] = row["judgeId"]
            
            
            source_text = self.extract_source(row["srclang"], row["testset"], row["srcIndex"])
            source = SimpleSentence(source_text)
            
            translations = self.get_translations(row)
            
            parallelsentence = ParallelSentence(source, translations, None, attributes)
            parallelsentences.append(parallelsentence)
        return parallelsentences
            
            
            
    def convert_languages(self,row):
        row["srclang"] = LANGUAGES[row["srclang"]]
        row["trglang"] = LANGUAGES[row["trglang"]]  
        return row
            
    def get_translations(self, row):
        
        translations = []
        for i in range(1, self.systems_num + 1 ):
            system_id = row["system%dId" % i]
            attributes = {"system": system_id, 
                      "rank": row["system%drank" % i] }
            translation_string = self.extract_translation(system_id, row["srclang"], row["trglang"], row["srcIndex"], row["testset"])
            
            translations.append(SimpleSentence(translation_string, attributes))
        return translations
    
    
    def extract_translation(self, system, srclang, trglang, sentence_index, testset):
        langpair = "%s-%s" % (srclang, trglang)
        sentence_index = int(sentence_index)
        path = self.config.get("data","path")
        result = ''
        fieldmap={ 'path' : path ,
                'langpair' : langpair,
                'testset' : testset,
                'system' : system } 
                
        if system != '_ref':
            pattern_submissions = self.config.get('data', 'pattern_submissions')
            try:
                #print "trying to access %s" % (pattern_submissions % fieldmap)
                filename = codecs.open(pattern_submissions % fieldmap, 'r', 'utf-8')
            except:
                sys.stderr.write("possibly system %s is not provided for this language pair %s and testset %s, please filter it out through config file to proceed\n" % (system, langpair, testset))
                return ""
                #sys.exit() 
            translations = list(enumerate(filename))
            for (index, sentence) in translations:
                if index+1 == sentence_index:
                    result = sentence
                    break
        else:
            result = self.extract_source(trglang, None, sentence_index)

        return result

    
    def extract_source(self, srclang, testset, sentence_index ):
        path = self.config.get("data","path")
        sentence_index = int(sentence_index)
        pattern_sourceref = self.config.get("data","pattern_sourceref")
        pattern_fields = {"path": path,
                          "srclang": srclang,
                          "testset": testset}
        full_filename = pattern_sourceref % pattern_fields
        translations = list(enumerate(codecs.open(full_filename, 'r', 'utf-8')))
        result = ''
        for (index, sentence) in translations:
            if index+1 == sentence_index:
                result = sentence
                break
        if result =='':
            print "Cannot resolve sentence [%d] in file %s" % (sentence_index, full_filename)
        return result
    
    
    def get_system_names(self, row):
        system_names=[]
        for i in range(1, self.systems_num + 1 ):
            try:
                system_names.append(row["system%dId" % i] )
            except:
                sys.stderr.write("Could not parse system Id %d\n" % i)
        
            
    def get_task_data(self, row):
        task_details = row["task"].split(' ')
        row["task"] = task_details[0]
        #get language data
        [row["srclang"], row["trglang"]] = task_details[0].split('-')
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
        sys.stderr.write("Sentences read, proceeding with writing XML")
        xmlwriter = XmlWriter(parallelsentences)
        filename = config.get("output", "filename")
        xmlwriter.write_to_file(filename)
        sys.stderr.write("Done")
        
                  
            
            
            
            
            
              
        
    
    
    
    
        