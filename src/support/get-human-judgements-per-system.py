# -*- coding: utf-8 -*-

import sys
import codecs

LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr'
             }

###DO THIS
SUBMISSIONFILES = "/home/elav01/taraxu_data/wmt08-humaneval-data/submissions/newssyscombtest2010.%s.%s'"
SYSTEM1 = ['RBMT3']
SYSTEM2 = ['UEDIN']

CSV_MAPPING_SCORE = { 1 : 16,
                             2 : 17,
                             3 : 18,
                             4 : 19,
                             5 : 20  }


""" 
Utility function to check whether to lists intersect 
"""
def intersect(a, b):
     return ( list (set(a) & set(b)) )


"""
Get the actual sentence text, given its sentence ID
""" 
def extract_sentence(path, system, direction, sentence_index):
    result = ''
    if system != '_ref':
        translations = list(enumerate(codecs.open( SUBMISSIONFILES %
                               (path, direction, system), 'r', 'utf-8')))
        for (index, sentence) in translations:
            if index == sentence_index:
                result = sentence
                break
    else:
        result = extract_ref(path, direction[-2:], sentence_index)

    return result

def extract_source(path, language, sentence_index):
    translations = list(enumerate(codecs.open('%s/newssyscombtest2010.%s' %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def extract_ref(path, language, sentence_index):
    translations = list(enumerate(codecs.open('%s/newssyscombtest2010.%s' %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def write_rankings(source, rankings, file_gt, file_lt, file_eq):
    rank_g = rankings[0]
    rank_d = rankings[1]
    
    
    file = None
    if rank_g < rank_d:
        file = file_gt
    elif rank_g == rank_d:
        file = file_eq
    else:
        file = file_lt

    file.write('SOURCE:\t%s\n' % source)
    for (rank, sys, sent) in rankings:
        if sys == 'dfki':
            sys = '***dfki***'
        elif sys == 'onlineB':
            sys = '***google***'
    file.write('%s:\t%s\t->\t %s\n' % (rank.strip(), sys, sent))
    return None

def create_evaluation(judgments, path):
    out_gt = codecs.open('evaluations_gt', 'w', 'utf-8')
    out_lt = codecs.open('evaluations_lt', 'w', 'utf-8')
    out_eq = codecs.open('evaluations_eq', 'w', 'utf-8')
    for line in judgments:
        fields = line.split(',')
        src = LANGUAGES[fields[0]]
        tgt = LANGUAGES[fields[1]]
        dir = src + '-' + tgt
        index = int(fields[2])
        system = []
        system[1] = fields[7]
        system[2] = fields[9]
        system[3] = fields[11]
        system[4] = fields[13]
        system[5] = fields[15]
        
        #we are interested in the comparison of two systems groups. First check whether they both exist 
        desiredsystem1 = intersect( system , SYSTEM1)
        desiredsystem2 = intersect( system , SYSTEM2)
        
        #check if both lists have contents 
        if ( desiredsystem1 and desiredsystem2 ):
            
            #get the indices of each system
            desiredsystemid1 = system.index(desiredsystem1 )
            desiredsystemid2 = system.index(desiredsystem2 )
         
            sentence1 = extract_sentence(path, desiredsystem1, dir, index)
            sentence2 = extract_sentence(path, desiredsystem2, dir, index)
            
            
            
            entries = []
            entries.append((CSV_MAPPING_SCORE[desiredsystemid1], system[desiredsystemid1], sentence1))
            entries.append((CSV_MAPPING_SCORE[desiredsystemid2], system[desiredsystemid2], sentence2))
            #entries.sort()
            source = extract_source(path, src, index)
    
            write_rankings(source, entries, out_gt, out_lt, out_eq)

    out_gt.close()
    out_lt.close()
    out_eq.close()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'USAGE: %s JUDGMENTS.CSV PATH' % sys.argv[0]
        print '\tpath = path to folder with evaluation raw data'
    else:
        input = codecs.open(sys.argv[1], 'r', 'utf-8')
        path = sys.argv[2]
        create_evaluation(input, path)
