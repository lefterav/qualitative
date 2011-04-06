import csv
import ConfigParser
import os
import sys
import codecs



class WMTEvalReader:
    def __init__(self, csvfilename, config):
        self.config = config
        fieldnames = config.get("format","fieldnames").split(',')
        csvfile = open(csvfilename)
        self.reader =  csv.DictReader(csvfile, fieldnames)
        self.systems_num = config.getint("format","systems_num")
        
    def parse(self):
        for row in self.reader:
            if self.test2008:
                row = self.get_task_data(row)
                   
            
            #skip this row if it doesn't match filtering criteria
            if not self.check_filters(row):
                continue
            
            source_text = self.extract_source(row["srclang"], None, row["srcIndex"])
    
    
            
    def get_translations(self, row):
        translations = []
        for i in range(0, self.systems_num + 1 ):
            attributes = {"system": row["system%dId"] % i, 
                      "rank": row["system%drank"] % i }
            translations.append(attributes)
        return translations
    
    
    def extract_translation(self, system, srclang, tgtlang, sentence_index, testset):
        langpair = "%s,%s" % (srclang, tgtlang)
        path = self.config.get("data","path")
        result = ''
        fieldmap={ 'path' : path ,
                'langpair' : langpair,
                'testset' : testset,
                'system' : system } 
                
        if system != '_ref':
            pattern_submissions = self.config.get('data', 'pattern_submissions')
            try:
                filename = codecs.open(pattern_submissions % fieldmap, 'r', 'utf-8')
            except:
                sys.stderr.write("possibly system %s is not provided for this language pair %s and testset %s, please filter it out through config file to proceed\n" % (system, langpair, testset))
                return ""
                #sys.exit() 
            translations = list(enumerate(filename))
            for (index, sentence) in translations:
                if index == sentence_index:
                    result = sentence
                    break
        else:
            result = self.extract_source(tgtlang, None, sentence_index)

        return result

    
    def extract_source(self, srclang, testset, sentence_index ):
        path = self.config.get("data","path")
        pattern_sourceref = self.config.get("data","pattern_sourceref")
        pattern_fields = {"path": path,
                          "srclang": srclang,
                          "testset": testset}
        full_filename = pattern_sourceref % pattern_fields
        translations = list(enumerate(codecs.open(full_filename, 'r', 'utf-8')))
        result = ''
        for (index, sentence) in translations:
            if index == sentence_index:
                result = sentence
                break
        if result =='':
            print "Cannot resolve sentence [%d] in file %s" % (sentence_index, full_filename)
        return result
    
    
    def get_system_names(self, row):
        system_names=[]
        for i in range(0, self.systems_num + 1 ):
            try:
                system_names.append(row["system%dId" % i] )
            except:
                sys.stderr.write("Could not parse system Id %d" % i)
        
            
    def get_task_data(self, row):
        task_details = row["task"].split(' ')
        row["task"] = task_details[0]
        #get language data
        [row["srclang"], row["tgtlang"]] = task_details[0].split('-')
        #get dataset
        row["testset"] = task_details[2]
        return row

    def check_filters(self, row):
        #keep that in memo
        system_names = self.get_system_names(row)
        for (field_name, value) in self.config.items("filters_include"):
            try:
                #use replacement pattern to include only rows that have required systems
                if field_name.startswith("system"):
                    
                    if value not in system_names:
                        return False    
                #process the rest of the namely specified fields (e.g. srclang)                         
                if row[field_name] != value:
                    return False
            except:
                sys.stderr.write("skipping filter [%s]:%s, sth went wrong" % (field_name, value) )
                
        for (field_name, value) in self.config.items("filters_exclude"):
            try:
                if field_name.startswith("system"):
                    if value in system_names:
                        return False 

                #process the rest of the namely specified fields (e.g. srclang)                         
                if row[field_name] == value:
                    return False
            except:
                sys.stderr.write("skipping filter [%s]:%s, sth went wrong" % (field_name, value) )
    
        return True
             
            
            
            
            
            
            
            
            
              
        
    
    
    
    
        