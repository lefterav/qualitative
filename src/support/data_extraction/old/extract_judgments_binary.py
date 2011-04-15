# -*- coding: utf-8 -*-

##cd ~/taraxu_data/wmt08-humaneval-data; python extract_judgments08-onefile.py judgments_wmt08_final_sorted.csv  .


"""
This scripts extracts the data from the wmt08 evaluation, focusing on the pairs of Lucy and other scripts 

"""

import sys
import codecs
import xml.dom.minidom
import ConfigParser, os
import string
import math
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
from io.output.xmlwriter import XmlWriter


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


#PTRN_SUBMISSIONS = '%s/submissions/%s.%s.%s'

PTRN_SOURCEREF = '%s/src-ref/%s.%s'

SYSTEMSET1 = ['rbmt3']
SYSTEMSET2 = ['uedin' , 'limsi' , 'saar' , 'liu']



#if you add constituents, bear in mind that you need to resolve the constituents ID somewhere
#different than how it is done with full sentences
TYPES = ['RANK']

""" 
Utility function to check whether two lists intersect 
"""
def intersect(a, b):
    return ( list (set(a) & set(b)) )
 
 

def extract_sentence(path, system, langpair, sentence_index, testset, config):
    result = ''
    fieldmap={ 'path' : path ,
            'langpair' : langpair,
            'testset' : testset,
            'system' : system } 
            
    if system != '_ref':
        pattern_submissions = config.get('data', 'pattern_submissions')
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
        result = extract_ref(path, langpair[-2:], sentence_index)

    return result


def extract_source(path, language, sentence_index, testset, config):
    PTRN_SOURCEREF=config.get("data","pattern_sourceref")
    translations = list(enumerate(codecs.open(PTRN_SOURCEREF %
                               (path,  testset, language), 'r', 'utf-8')))
    result = ''
    for (index, sentence) in translations:
        if index == sentence_index:
            result = sentence
            break
    if result =='':
        print "Cannot resolve sentence [" + str(sentence_index) + "] in file " + PTRN_SOURCEREF % (path,  testset, language)
    return result


def extract_ref(path, language, sentence_index, config):
    PTRN_SOURCEREF=config.get("data","pattern_sourceref")    
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
def write_rankings_XML (source, rankings, docXML, langsrc, langtgt, testset, index , rank ):
    #add a sentence to the XML
    judgedsentenceXML = docXML.createElement("judgedsentence")
    judgedsentenceXML.setAttribute("id", index)
    judgedsentenceXML.setAttribute("langsrc", langsrc)
    judgedsentenceXML.setAttribute("langtgt", langtgt)
    judgedsentenceXML.setAttribute("testset", testset)
    judgedsentenceXML.setAttribute("rank", str(rank))
    docXML.childNodes[0].appendChild(judgedsentenceXML)
    
    #add the text of the source sentence to the XML
    srcXML = docXML.createElement("langsrc")
    judgedsentenceXML.appendChild (srcXML)
    srctextXML = docXML.createTextNode(source)
    srcXML.appendChild(srctextXML)
    
    for (score, sys, sent) in rankings:
    
        #add the text of the target sentence to the XML
        tgtXML = docXML.createElement("langtgt")
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

def scores_get_rank_unit(score1, score2):
    score1 = int(score1)
    score2 = int(score2)
    if (score1 < score2) :
        rank = 1
    elif (score1 > score2) :
        rank = -1
    else :
        rank = 0
    return rank

"""
    Breaks a list of elements into pairs, just by coupling every item to its adjacent
    @param list: A list of elements that will be broken into pairs
    @return: a list of tuples of items 
"""
def get_pairs_pairwise(list):
    previousitem = None
    pairs = []
    for item in list:
        if previousitem:
            #keep tuples in items sorted alphabetically
            sort_list = [previousitem, item]
            sort_list.sort(key=string.lower) 
            pairs.add( tuple(sort_list) )
    pairs.sort(key=string.lower)
    return pairs
            
"""
    Breaks a list of elements into pairs, by providing every possible combination of pairs
    @param list: A list of elements that will be broken into pairs
    @return: a list of tuples of items 
"""
def get_pairs_combinatorial(list):
    pairs = []
    for i in range(len(list)-1):
        for j in range(i+1,len(list)):
            sort_list = [list[i], list[j]]
            sort_list.sort(key=string.lower)
            pairs.append( tuple(sort_list))
    pairs.sort()
    return pairs
            
"""
    Some fields in WMT08 and WMT09 need to be expanded, because they are separated with space instead of comma
    @param list: A list of elements that will be broken into pairs
    @return: a list of tuples of items 
"""
def expand_field(fields, colposition, separator):

    col1 = fields[colposition].split(separator)
    #task = col1[0]
    adaptedfields = fields[0:colposition]
    adaptedfields.extend(col1)
    adaptedfields.extend(fields[colposition+1:len(fields)])
    return adaptedfields

        
            
"""
    Basic method that does the processing of a set of lines, as released by the shared evaluation tasks
    @param judments: a list of lines (string) containing data per judgment. We presuppose that they are sorted by systemid and sentenceid
    @param path: the local path where output files should be written
    @param config: an object produced by a Configparser containing formatting parameters 
"""
def parse_sentences(judgments, path, config):
    
    parallelsentences = []
    ##out = codecs.open('evaluations_all', 'w', 'utf-8')
    
    #initialize buffer variables to be used in the loop
    cur_desiredsystem1 = ''
    cur_desiredsystem2 = ''
    cur_langpair = None
    cur_testset = None
    cur_index = None
    cur_langsrc = ''
    cur_langtgt =''
    score_sum = 0
    entry_id = 0
    accepted_id =0
    avg_rank = 0
    firstline = True
    
    SYSTEM_FIELDS = config.get("format", "systems").split(",")
    CSV_MAPPING_SCORE = config.get("format", "scores").split(",")
    
    sentence_judgments = {}
    
    """
        This loop works a bit ugly, in order to overcome the fact that a sentence may have many contradictory judgments: 
        Since the input is sorted by task, pair, sentence id, we gather rankings for as long these remain the same in the loop, 
        and when they change, we call the function that calculates the average rank and prints it to the file
    """
    for line in judgments:
        #general counter
        entry_id += 1
        separator = config.get("format", "separator").replace("\s", " ").replace("\\t", u"\t") #take care of separators that are a space
        fields = line.split(separator)
        
        #Jump first line (header)
        if firstline:
            firstline=False
            continue
        
        if fields<5:
            sys.stderr.write("Broken line. Check separator")
            continue
            

        
        
        if config.getboolean("format", "col_task_span"):
            #First column has a lot of data separated with spaces
            separator = config.get("format", "col_task_separator").replace("\s", " ")
            colposition = config.getint("format", "col_task")
            try:
                fields=expand_field(fields, colposition, separator)
            except:
                continue

        
        if config.getboolean("format", "col_langpair_span"):
            #extract the langsrc and trg language from language pair
            colposition = config.getint("format", "col_langpair")
            language_pair = fields[colposition].split('-')
            #fields = expand_field(fields, colposition, '')
            
       
        if len(language_pair)<2:
            continue
        
        langsrc = language_pair[0]
        langtgt = language_pair[1]
        try:
            langsrc = LANGUAGES[language_pair[0]]
            langtgt = LANGUAGES[language_pair[1]]
        except:
            continue   
        langpair = "%s-%s" % (langsrc, langtgt)
    
        testset_name = fields[config.getint("format", "testset")]
        testset = config.get('testsets', testset_name)
        type = fields[ config.getint("format", "type") ]
        index = int(fields[ config.getint("format", "index") ])
        
        if not cur_index:
            cur_index = index
        if not cur_langpair:
            cur_langpair = langpair
            cur_langsrc = langsrc
            cur_langtgt = langtgt
        if not cur_testset:
            cur_testset = testset
            
        if not ( langpair == cur_langpair and testset == cur_testset and index == cur_index ):
            #if len (parallelsentences)> 0:
            #    continue;  
            psentences = process_sentence_judgments (sentence_judgments, cur_langpair, cur_langsrc, cur_langtgt, cur_index, cur_testset, path, config.getboolean("filters-exclude","zero-rank"))
            parallelsentences.extend( psentences )   
   
            #update sentence and buffer variables
            cur_langpair = langpair
            cur_langsrc = langsrc
            cur_langtgt = langtgt
            cur_index = index
            print "\n" , index ,
            cur_testset = testset
            sentence_judgments = {}

            
        #apply filters
        if config.get("filters", "types"):
            acceptedtypes = config.get("filters", "types").split(",")
            if type not in acceptedtypes:
                continue
            
        if config.get("filters", "langsrc"):
            acceptedlangsrc = config.get("filters", "langsrc").split(",")
            if langsrc not in acceptedlangsrc:
                continue
        
        if config.get("filters", "langsrc"):
            acceptedlangtgt = config.get("filters", "langtgt").split(",")
            if langtgt not in acceptedlangtgt:
                continue
        
        if config.get("filters-exclude", "langsrc"):
            unacceptablelangsrc = config.get("filters-exclude", "langsrc").split(",")
            if langsrc in unacceptablelangsrc:
                continue
        
        if config.get("filters-exclude", "langsrc"):
            unacceptablelangtgt = config.get("filters-exclude", "langtgt").split(",")
            if langtgt in unacceptablelangtgt:
                continue
        


        
        system_names = []
        systems_count = 0
        
        for system_field in SYSTEM_FIELDS:
            try:
                system_name = fields[int(system_field)]
                if config.get("filters-exclude", "systems"):
                    unacceptablesystems = config.get("filters-exclude", "systems").split(",")
                    if system_name in unacceptablesystems:
                        continue
                system_names.append( system_name )
                systems_count += 1
            except:
                system_names.append("")
        
        #method for getting pairwise all the system outputs for this source sentence
        system_pairs = get_pairs_combinatorial(system_names)
        
        
        #a loop that will be able to process a list of pairs 
        for (desiredsystem1, desiredsystem2) in system_pairs:
            if desiredsystem1 == "" or desiredsystem2 == "":
                continue
            #get the indices of each system
            desiredsystemid1 = int(system_names.index(desiredsystem1))
            desiredsystemid2 = int(system_names.index(desiredsystem2))
                
            #get the scores given, in the columns relevant to each system
            score1 = (fields[int(CSV_MAPPING_SCORE[desiredsystemid1])])
            score2 = (fields[int(CSV_MAPPING_SCORE[desiredsystemid2])])
    
            rank = scores_get_rank_unit(score1, score2)
            
            #add the rank into a lexicon, so that majority voting can be applied when more than one judgments for this pair
            #the lexicon has a scope just of the sentence
            if sentence_judgments.has_key((desiredsystem1, desiredsystem2)):
                sentence_judgments[(desiredsystem1, desiredsystem2)] = sentence_judgments[(desiredsystem1, desiredsystem2)] + rank
            else:
                sentence_judgments[(desiredsystem1, desiredsystem2)] = rank
    
    
    
    #process the last entry also
    psentences = process_sentence_judgments (sentence_judgments, cur_langpair, cur_langsrc, cur_langtgt, cur_index, cur_testset, path, config.getboolean("filters-exclude","zero-rank"))
    parallelsentences.extend(psentences)        
    #update sentence and buffer variables  
 
    print "accepted judgments", accepted_id
    
    return parallelsentences


def process_sentence_judgments (sentence_judgments, cur_langpair, cur_langsrc, cur_langtgt, cur_index, cur_testset, path, exclude_zero):
    #loop through the ranked sentence pairs
    parallelsentences=[]
    for (desiredsystem1,desiredsystem2) in sentence_judgments.keys():
        rank = sentence_judgments[(desiredsystem1,desiredsystem2)]
        #keep only the sign, indicating the decision of majority voting
        
        
        #skip sentences with balanced or equal judgments, if specified
        if rank == 0 and exclude_zero:
            continue
        
        rank = math.copysign(1, rank)
        
        #browse special file for the sentence text
        target1_string = extract_sentence(path, desiredsystem1, cur_langpair, cur_index, cur_testset, config)
        target2_string = extract_sentence(path, desiredsystem2, cur_langpair, cur_index, cur_testset, config)
        
        target1 = SimpleSentence(target1_string, {'system': desiredsystem1 })
        target2 = SimpleSentence(target2_string, {'system': desiredsystem2 })
        target = [target1, target2]
        
        source_string = extract_source(path, cur_langsrc, cur_index, cur_testset, config)
        source = SimpleSentence(source_string)

        parallelsentence = ParallelSentence (source, target)
        parallelsentence.set_langsrc(cur_langsrc)
        parallelsentence.set_langtgt(cur_langtgt)
        parallelsentence.set_id(cur_index)
        parallelsentence.add_attributes({'testset' : cur_testset , 'rank' : str(int(rank))})
        parallelsentences.append(parallelsentence)
        print ".",
    return parallelsentences   
    
    



if __name__ == "__main__":
    

    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        config = ConfigParser.RawConfigParser()
        config.read([ sys.argv[1] ])
        filename = config.get("data", "filename")
        path = config.get("data", "path")
        input = codecs.open(path+filename, 'r', 'utf-8')
        parallelsentences = parse_sentences(input, path, config)
        xmlwriter = XmlWriter(parallelsentences)
        filename = config.get("output", "filename")
        xmlwriter.write_to_file(path+filename)
            
