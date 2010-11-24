# -*- coding: utf-8 -*-




import sys
import codecs


"""
Global Settings: 
This sections contains general settings for fixed mappings etc. in order to be used
for this type of input file. 
"""

#Language mapping, needed for browsing the correct test/source/ref file
LANGUAGES = {
             'Spanish' : 'es',
             'English' : 'en',
             'Czech' : 'cz',
             'German' : 'de',
             'French' : 'fr',
             'Hungarian' : 'hu'
             }

#Several test sets may be part of the task
TESTSETS = { 
             'Europarl' : 'test2008',
             'News' : 'newstest2008',
             'Commentary' : 'nc-test2008'
            }


PTRN_SUBMISSIONS = '%s/submissions/%s.%s.%s'
PTRN_SOURCEREF = '%s/src-ref/%s.%s'

SYSTEMSET1 = ['rbmt3']
SYSTEMSET2 = ['uedin' , 'limsi' , 'saar' , 'liu']

CSV_MAPPING_SCORE =[ -1000 , 6, 9, 12, 15, 18 ]

#if you add constituents, bear in mind that you need to resolve the constituents ID somewhere
#different than how it is done with full sentences
TYPES = ['RANK']

""" 
Utility function to check whether two lists intersect 
"""
def intersect(a, b):
    return ( list (set(a) & set(b)) )
 
 

def extract_sentence(path, system, direction, sentence_index, testset):
    result = ''
    if system != '_ref':
        translations = list(enumerate(codecs.open(PTRN_SUBMISSIONS %
                               (path, direction, testset, system), 'r', 'utf-8')))
        for (index, sentence) in translations:
            if index == sentence_index:
                result = sentence
                break
    else:
        result = extract_ref(path, direction[-2:], sentence_index)

    return result

def extract_source(path, language, sentence_index, testset):
    translations = list(enumerate(codecs.open(PTRN_SOURCEREF %
                               (path,  testset, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    if result =='':
        print "Cannot resolve sentence " + str(sentence_index) + " in file " + PTRN_SOURCEREF % (path,  testset, language)
    return result

def extract_ref(path, language, sentence_index):
    translations = list(enumerate(codecs.open(PTRN_SOURCEREF %
                               (path, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    return result

def write_rankings(source, rankings, file_gt, file_lt, file_eq, index):
    rank_g = 0
    rank_d = 0
    for (rank, sys, sent) in rankings:
        if sys in SYSTEMSET1:
            rank_d = int(rank)
        elif sys in SYSTEMSET2:
            rank_g = int(rank)
            
        file = None
        if rank_g < rank_d:
            file = file_gt
        elif rank_g == rank_d:
            file = file_eq
        else:
            file = file_lt
        
        file.write('%s\tsource\t%s' % (index, source))
        for (rank, sys, sent) in rankings:
            #if sys == 'rbmt3':
            #    sys = '***Lucy***'
            #elif sys == 'uedin':
            #    sys = '***uedin***'
            file.write('%s\t%s\t%s' % (rank, sys, sent))
    return None


"""
    Manages a dictionary, which sorts the ranking scores per sentence key
"""
def sort_new_judgment( dic, key, rank ):
    if key in dic:
        #add to the existing list of ranking scores
        entry_to_extend = dic[key]
        entry_to_extend.append(rank)
    else:
        #initialize a new list with ranking scores
        new_entry = [rank]
        dic[key] = new_entry
    return dic
        

def create_evaluation(judgments, path):

    out_gt = codecs.open('evaluations_gt', 'w', 'utf-8')
    out_lt = codecs.open('evaluations_lt', 'w', 'utf-8')
    out_eq = codecs.open('evaluations_eq', 'w', 'utf-8')
    
    
    sorted_judgments = {};
    
    for line in judgments:
        
        fields = line.split(',')
        
        #Jump first line
        if not fields[0]=='TASK':
        
            #First column has a lot of data separated with spaces
            col1 = fields[0].split(' ')
            #task = col1[0]
            
            #extract the src and trg language from language pair
            language_pair = col1[1].split('-')
            
            
            if not ( "All" in language_pair ):
                
                src = LANGUAGES[language_pair[0]]
                tgt = LANGUAGES[language_pair[1]]
                dir = src + "-" + tgt
            
                testset = TESTSETS[col1[2]]
                
                type = fields[1]
                       
                index = int(fields[2])
                
                entries = []
                
                system= [ '', '','','','','']
                system[1] = fields[5]
                if len(fields)>8:
                    system[2] = fields[8]
                if len(fields)>11:
                    system[3] = fields[11]
                #avoid empty indices, when less than 5 judgemnts
                if len(fields)>14:
                    system[4] = fields[14]
                if len(fields)> 17:
                    system[5] = fields[17]
                
                #debug print
               
                
                
                #we are interested in the comparison of two systems groups. First check whether they both exist 
                desiredsystem1 = intersect( system , SYSTEMSET1)
                desiredsystem2 = intersect( system , SYSTEMSET2)
                
               
                
                #check if both lists have contents 
                if ( desiredsystem1 and desiredsystem2 and (type in TYPES)):
                    
                    #get the indices of each system

                    desiredsystemid1 = int (system.index(desiredsystem1[0] ))
                    desiredsystemid2 = int (system.index(desiredsystem2[0] ))
                    
                    #get the scores given, in the columns relevant to each system
                    score1 = (fields[CSV_MAPPING_SCORE[desiredsystemid1]])
                    score2 = (fields[CSV_MAPPING_SCORE[desiredsystemid2]])

                    #key1 = [desiredsystem1[0], dir, index, testset]
                    #sorted_judgments = sort_new_judgment(sorted_judgments, key1, score1)
                    
                    #key2 = [desiredsystem2[0], dir, index, testset]
                    #sorted_judgments = sort_new_judgment(sorted_judgments, key2, score2)

                    #browse special file for the sentence text
                    sentence1 = extract_sentence(path, desiredsystem1[0], dir, index, testset)
                    sentence2 = extract_sentence(path, desiredsystem2[0], dir, index, testset)
                    
                    entries = []
                    
                    entries.append((score1, desiredsystem1[0], sentence1))
                    entries.append((score2, desiredsystem2[0], sentence2))
                    
                    #make sure they always appear in the same order (not sure if needed)
                    #entries.sort()
                    source = extract_source(path, src, index, testset)
            
                    write_rankings(source, entries, out_gt, out_lt, out_eq, dir+":"+testset+":"+str(index))


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
