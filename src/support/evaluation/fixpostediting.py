'''
Created on Sep 5, 2011
@author: Elefherios Avramidis

This script has been created in order to fix the wrongly assigned translator's
system preferences for the post-editing task of the TaraXU 1st Evaluation Round.
Since the system used for post-editing has been wrongly stored into the
database, we try to retrieve this information, by picking up the system output
with the lowest levenshtein distance with the post-edited entry. Just to make it
clear, we also include Levenshtein difference (lev-dif) with the next possible
system. I.e. lev-dif of 1 may have led to a slightly uncertain selection.

USAGE: 
from ... import fix_dirs
fix_dirs(["/path/to/directory1", "/path/to/directory2" ])

specify the directories where ranking.xml and editing.xml files reside. 

'''

from io.input.rankreader import RankReader
from io.input.posteditingreader import PosteditingReader
from io.output.posteditingwriter import PosteditingWriter
from support.evaluation.levenshtein import levenshtein_tok
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import os
import re
import sys

def fix( rankingfile, posteditingfile, fixedfile):
    #read the files into the memory
    rankingset = RankReader(rankingfile).get_dataset()
    editedset = PosteditingReader(posteditingfile).get_dataset()
    
    #editing set contains only text from one erroneously stored system
    #so by merging based on the sentence id, we get the rest of the sentences:
    editedset.merge_dataset(rankingset, {}, ["sentence_id"])

    rankingset = None
    
    fixed_parallelsentences = []
    uncertain_decisions = 0
    
    for ps in editedset.get_parallelsentences():
        system_outputs = []
        postedited_string = ""
        
        for s in ps.get_translations():
            if s.get_attribute("system") == 'post-edited':
                postedited_sentence = s
                postedited_string = s.get_string()
                (postedited_string, postedited_comment) = re.findall("(.*)\n{0,2}(.*)", postedited_string)[0]
            else:
                if s.get_attribute("name") != "google":
                    origin = ""
                    try:
                        #don't store the sentence if it originates from the faulty storage
                        origin = s.get_attribute("origin") == "post-editing" 
                    except:
                        pass
                    if origin != "post-editing":
                        system_outputs.append(s)
            
        lev_values = []
        
        #get lev for each system output given the postedited reference
        for system_output in system_outputs:
            lev_value = levenshtein_tok(str(postedited_string), str(system_output.get_string())) 
            #print lev_value
            lev_values.append(lev_value)
            system_output.add_attribute('lev', lev_value)
            
        min_lev_value = min(lev_values)
        
        #gather the systems that have equal lev
        best_system_outputs = []
        lev_diffs = []
        for system_output in system_outputs:
            if system_output.get_attribute('lev') == min_lev_value:
                try:
                    system_output.del_attribute("origin")
                except:
                    pass
                system_output.del_attribute("system")
                best_system_outputs.append(system_output)
            else: #collect the differences to find the minimum
                lev_diffs.append(int(system_output.get_attribute('lev')) - min_lev_value)
                
        
        if not lev_diffs:
            lev_diffs = [0]
        #this will show the certainty
        min_lev_diff = min(lev_diffs)
        
        
        #now create the objects to be sent to the writer
        postedited_sentence.del_attribute("system")
        ps_attributes = ps.get_attributes()
        ps_attributes["lev-diff"] = min_lev_diff
        fixed_parallelsentence = ParallelSentence(ps.get_source(), best_system_outputs, postedited_sentence, ps_attributes) 
        fixed_parallelsentences.append(fixed_parallelsentence)
        
        
        if len(best_system_outputs) > 1 : 
            uncertain_decisions += 1
        
        
        
#        print "post:" , postedited_string
#        for system_output in best_system_outputs:
#            print "%s [%f][%s]: %s" % (ps.get_attribute("id"), system_output.get_attribute("lev"), system_output.get_attribute("system"), system_output.get_string())
#            
#        print "-----"
#        for system_output in system_outputs:
#            print "[%f][%s]: %s" % ( system_output.get_attribute("lev"), system_output.get_attribute("system"), system_output.get_string())
#        
#        print min_lev_diff

    testset_atts = {"uncertain-lev-choices" : uncertain_decisions }
    print uncertain_decisions , "uncertain decisions"
    print "writing to file", fixedfile
    PosteditingWriter(fixed_parallelsentences, testset_atts).write_to_file(fixedfile)
    
            

def fix_dirs(dirs):
    """
    Create pairs of complementary ranking and editing files for the same tasks
    and fix them with the function above
    """
    
    
    rankingfiles = []
    editingfiles = []
    
    files = ["%s/%s" % (dir, filename) for dir in dirs for filename in (os.listdir(dir))]

    for filename in files:
        if filename.endswith('ranking.xml'):
            rankingfiles.append(filename)
        elif filename.endswith('editing.xml'):
            editingfiles.append(filename)
    
    filenames = []
    
    #separate files for the same datasets must be matched based on their name 
    for editingfile in editingfiles:
        try:
            (path, task_id, subtask, set_name) = re.findall("(.*)/(\d+)-(\[[0-9A-KM-Z]+\])\s(.*)-editing.xml", editingfile)[0]
            found = False
            for rankingfile in rankingfiles:
                try:
                    (r_path, r_task_id, r_subtask, r_set_name) = re.findall("(.*)/(\d+)-(\[\d+\])\s(.*)-ranking.xml", rankingfile)[0]
                except:
                    continue
                
                if r_set_name == set_name: 
                    
                    #also suggest the name for the output file
                    print "matched!"
                    fixedfile = "%s/%s-[L] %s-editing.xml" % (path, task_id, set_name)
                    filenames.append((rankingfile, editingfile, fixedfile))
                    found = True
                    break
            if not found :
                print "Didn't find a match for " , editingfile
        except:
            print "error matching" , editingfile
            pass
    
    if len(filenames) < len(editingfiles):
        print "Didn't match everythin", len(filenames) , len(editingfiles)
        
    for (rankingfile, editingfile, fixedfile) in filenames:
        fix(rankingfile, editingfile, fixedfile)
        
        

filenames = [arg for arg in sys.argv[1:]]
fix_dirs(filenames)
    
    
    
        
#    editingfile = "/home/elav01/taraxu_data/r1/results/5-1-WMT08-de-en-editing.xml"
#    rankingfile = "/home/elav01/taraxu_data/r1/results/6-1-WMT08-de-en-ranking.xml"

#    fix(rankingfile, editingfile)  


                
                    
                       
        
        
        
