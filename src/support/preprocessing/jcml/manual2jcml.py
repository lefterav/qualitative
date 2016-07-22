'''
Convert from a csv file produced by Vivien Macketanz to a jcml file that can be fed
in the selection/ranking mechanism

Created on Jul 22, 2016

@author: lefterav
'''
import csv
from itertools import izip
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import sys
from dataprocessor.sax.saxps2jcml import IncrementalJcml

SRCLANG = "en"
TGTLANG = "de"
FIRST_COLUMN = 4

def get_parallelsentences(filename, errortype="generic_errors"):
    overall_index = 0
    csvfile = open(filename)
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    sheet_index = 0
    for row in csvreader:
        sheet_index += 1
        if sheet_index==1: 
            header = row
            continue
        overall_index += 1
        sentence_id = row[0]
        source_string = row[2]
        reference_string = row[-1]
        if sentence_id.strip()=="" or source_string.strip()=="" or reference_string.strip()=="":
            continue
                    
        try:
            phenomenon_count = int(row[3])
        except:
            continue
        
        a = iter(row[FIRST_COLUMN:-1])
        source = SimpleSentence(source_string, {errortype : phenomenon_count})
        reference = SimpleSentence(reference_string, {})
        
        this_translations = []
        i = 0
        offset = 0
        for translation_string, count in izip(a, a):
            if count=="":
                continue
            
            try:
                count = int(count)
            except:
                count = int(next(a))
                offset+=1
            
            system_name = header[i*2 + FIRST_COLUMN + offset]
            translation = SimpleSentence(translation_string, 
                                         {'rank' : phenomenon_count - count + 1, 
                                          'system' : system_name})
            this_translations.append(translation)
            i+=1        
        
        yield ParallelSentence(source, this_translations, reference, 
                               {'id' : sentence_id,
                                'langsrc' : SRCLANG,
                                'langtgt' : TGTLANG})


def convert_manual2jcml(source_filename, target_filename, writer=IncrementalJcml):
    parallelsentences = get_parallelsentences(source_filename)
    writer = writer(target_filename)
    writer.add_parallelsentences(parallelsentences)
    writer.close()


if __name__ == '__main__':
    convert_manual2jcml(sys.argv[1], sys.argv[2])
    
    