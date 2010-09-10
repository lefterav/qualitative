# -*- coding: utf-8 -*-

##cd ~/taraxu_data/wmt08-humaneval-data; python extract_judgments08-onefile.py judgments_wmt08_final_sorted.csv  .


'''
This scripts extracts the data from the wmt08 evaluation, focusing on the pairs of Lucy and other scripts 

'''

import sys
import codecs
import xml.dom.minidom


'''
Global Settings: 
This sections contains general settings for fixed mappings etc. in order to be used
for this type of input file. 
'''

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

''' 
Utility function to check whether two lists intersect 
'''
def intersect(a, b):
    return ( list (set(a) & set(b)) )
 
 

def extract_sentence(path, system, direction, sentence_index, testset):
    result = ''
    if system != '_ref':
        translations = list(enumerate(codecs.open(PTRN_SUBMISSIONS % (path, direction, testset, system), 'r', 'utf-8')))
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


def write_rankings_simple (source, rankings, file, index, rank):
    file.write('%s\t%s\t%s' % (index, rank, source))
    for (score, sys, sent) in rankings:
        file.write('%s\t%s\t%s' % (score, sys, sent))
        

#adds XML content to the root XML document
def write_rankings_XML (source, rankings, docXML, src, tgt, testset, index , rank ):
    #add a sentence to the XML
    judgedsentenceXML = docXML.createElement("judgedsentence")
    judgedsentenceXML.setAttribute("id", index)
    judgedsentenceXML.setAttribute("langsrc", src)
    judgedsentenceXML.setAttribute("langtgt", tgt)
    judgedsentenceXML.setAttribute("testset", testset)
    judgedsentenceXML.setAttribute("rank", str(rank))
    docXML.childNodes[0].appendChild(judgedsentenceXML)
    
    #add the text of the source sentence to the XML
    srcXML = docXML.createElement("src")
    judgedsentenceXML.appendChild (srcXML)
    srctextXML = docXML.createTextNode(source)
    srcXML.appendChild(srctextXML)
    
    for (score, sys, sent) in rankings:
    
        #add the text of the target sentence to the XML
        tgtXML = docXML.createElement("tgt")
        tgtXML.setAttribute("system", sys)
        judgedsentenceXML.appendChild (tgtXML)
        tgttextXML = docXML.createTextNode(sent)
        tgtXML.appendChild(tgttextXML)
    
    #add rank
    #rankXML = docXML.createElement("rank")
    #judgedsentenceXML.appendChild (rankXML)
    #rankvalueXML = docXML.createTextNode(str(rank))
    #rankXML.appendChild(rankvalueXML)
    
    
    
    
    return docXML    
    
    
    

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


'''
    Manages a dictionary, which sorts the ranking scores per sentence key
'''
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
        

def newXMLFile():
    doc = xml.dom.minidom.Document()
    # Create the <set> base element
    testset = doc.createElement("jcml")
    doc.appendChild(testset)    
    return doc

def writeXMLFile(doc, filename='evaluations_all.jcml'):
    file_object = codecs.open(filename, 'w', 'utf-8')
    file_object.write(doc.toprettyxml())
    file_object.close()  
    


def create_evaluation(judgments, path):
    
    docXML = newXMLFile()
    ##out = codecs.open('evaluations_all', 'w', 'utf-8')
    
    cur_desiredsystem1 = ''
    cur_desiredsystem2 = ''
    cur_dir = ''
    cur_testset = ''
    cur_index = 0
    cur_src = ''
    cur_tgt =''
    score_sum = 0
    entry_id = 0
    accepted_id =0
    avg_rank = 0
    
    
    '''
        This loop works a bit ugly, in order to overcome the fact that a sentence may have many contradictory judgments: 
        Since the input is sorted by task, pair, sentence id, we gather rankings for as long these remain the same in the loop, 
        and when they change, we call the function that calculates the average rank and prints it to the file
    '''
    for line in judgments:
        entry_id = entry_id+1
   
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
                #avoid empty indices, when less than 5 judgemnts
                if len(fields)>8:
                    system[2] = fields[8]
                if len(fields)>11:
                    system[3] = fields[11]
                if len(fields)>14:
                    system[4] = fields[14]
                if len(fields)> 17:
                    system[5] = fields[17]
                
                
                #we are interested in the comparison of two systems groups. First check whether they both exist 
                desiredsystem1 = intersect( system , SYSTEMSET1)
                desiredsystem2 = intersect( system , SYSTEMSET2)
                
                
                #check if both lists have contents 
                if ( desiredsystem1 and desiredsystem2 and (type in TYPES)):
                    accepted_id+=1
                    
                    #get the indices of each system
                    desiredsystemid1 = int (system.index(desiredsystem1[0] ))
                    desiredsystemid2 = int (system.index(desiredsystem2[0] ))
                        
                    
                    #get the scores given, in the columns relevant to each system
                    score1 = (fields[CSV_MAPPING_SCORE[desiredsystemid1]])
                    score2 = (fields[CSV_MAPPING_SCORE[desiredsystemid2]])

                    if (score1 < score2) :
                        rank = 1
                    elif (score1 > score2) :
                        rank = -1
                    else :
                        rank = 0
                        
                    #accumulate the judgments ranking
                    score_sum = score_sum + rank
                    
                    if not ( cur_desiredsystem1 == desiredsystem1[0] and cur_desiredsystem2 == desiredsystem2[0] and dir == cur_dir and testset == cur_testset and index == cur_index ) :
                        if score_sum > 0 :
                            avg_rank = 1
                        elif score_sum < 0 :
                            avg_rank = -1
                        else :
                            avg_rank = 0
                        
                        #print [entry_id, path, cur_desiredsystem1, cur_desiredsystem2, cur_dir, cur_index, cur_testset, score1, score2, avg_rank, cur_src]
                        if accepted_id>1 :
                            docXML = process_current_judgments_set(path, docXML, cur_desiredsystem1, cur_desiredsystem2, cur_dir, cur_index, cur_testset, score1, score2, avg_rank, cur_src, cur_tgt)
                        
                        
                        #update 
                        cur_desiredsystem1 = desiredsystem1[0]
                        cur_desiredsystem2 = desiredsystem2[0]
                        cur_dir = dir
                        cur_index = index
                        cur_testset = testset
                        cur_src = src
                        cur_tgt = tgt
                        score_sum =0 
                        avg_rank = 0
                                        
    #                if entry_id == len(judgments) :
    docXML = process_current_judgments_set(path, docXML, cur_desiredsystem1, cur_desiredsystem2, cur_dir, cur_index, cur_testset, score1, score2, avg_rank, cur_src, cur_tgt)
     
    print "accepted judgments", accepted_id
    writeXMLFile (docXML)
    return None



def process_current_judgments_set(path, docXML, cur_desiredsystem1, cur_desiredsystem2, cur_dir, cur_index, cur_testset, score1, score2, avg_rank, cur_src, cur_tgt):
    #browse special file for the sentence text
    
    
    
    sentence1 = extract_sentence(path, cur_desiredsystem1, cur_dir, cur_index, cur_testset)
    sentence2 = extract_sentence(path, cur_desiredsystem2, cur_dir, cur_index, cur_testset)
    
    entries = []
    
    entries.append((score1, cur_desiredsystem1, sentence1))
    entries.append((score2, cur_desiredsystem2, sentence2))
    
    #print to file
    source = extract_source(path, cur_src, cur_index, cur_testset)

    docXML = write_rankings_XML(source, entries, docXML,  cur_src, cur_tgt, cur_testset , str(cur_index), avg_rank)
    
    return docXML



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        print '\tpath = path to folder with evaluation raw data'
    else:
        input = codecs.open(sys.argv[1], 'r', 'utf-8')
        path = sys.argv[2]
        create_evaluation(input, path)
