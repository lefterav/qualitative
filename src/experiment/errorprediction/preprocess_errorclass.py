'''


Created on 11 Apr 2013

@author: Eleftherios Avramidis
'''

import os
from collections import namedtuple 
from db import retrieve_uid, db_add_entries

langpairs = [("de", "en"), ("en","de"), ("de","fr"), ("fr","de"), ("de","es"), ("es","de")]
testsets = ["wmt"] #"openoffice", "wmt", "cust"]
systems = ["moses", "lucy"]

directory_annotated = os.path.expanduser("~/taraxu_data/r2/evaluation/errorprediction/errorClassification/annotated")
directory_source = os.path.expanduser("~/taraxu_data/r2/evaluation/errorprediction/errorClassification")

directory_hyp = directory_source
directory_edit = directory_source

pattern_annotated = "{sourcelang}-{targetlang}.{testset}.{system}.sent-error-rates"
pattern_source = "{sourcelang}-{targetlang}.{testset}.{system}.source"
pattern_edit = "{sourcelang}-{targetlang}.{testset}.{system}.edit"
pattern_hyp = "{sourcelang}-{targetlang}.{testset}.{system}.hyp"

def get_filenames():
    tasks = []
    Task = namedtuple("Task", "sourcelang, targetlang, testset, system, filename_source, filename_hyp, filename_edit, filename_annotated")
    for sourcelang, targetlang in langpairs:
        for testset in testsets:
            for system in systems:
                
                task = Task(
                            sourcelang = sourcelang,
                            targetlang = targetlang,
                            testset = testset,
                            system = system,
                            
                            filename_source = os.path.join(directory_source, 
                                                              pattern_source.format(sourcelang=sourcelang,
                                                                                    targetlang=targetlang,
                                                                                       testset=testset,
                                                                                       system=system                                                                 
                                                                                       )
                                                              ),
                            
                            filename_hyp = os.path.join(directory_hyp, 
                                                              pattern_hyp.format(sourcelang=sourcelang,
                                                                                    targetlang=targetlang,
                                                                                       testset=testset,
                                                                                       system=system                                                                 
                                                                                       )
                                                              ),
            
                            filename_edit = os.path.join(directory_edit, 
                                                              pattern_edit.format(sourcelang=sourcelang,
                                                                                    targetlang=targetlang,
                                                                                       testset=testset,
                                                                                       system=system                                                                 
                                                                                       )
                                                              ),
                            
                            filename_annotated = os.path.join(directory_annotated, 
                                                              pattern_annotated.format(sourcelang=sourcelang,
                                                                                    targetlang=targetlang,
                                                                                       testset=testset,
                                                                                       system=system                                                                 
                                                                                       )
                                                              ),
                                        
                                        
                            )
                
                
                tasks.append(task)
                
    return tasks

    
        


def sync_erroclass_ids():
    dbentries = []  
    
    from featuregenerator.preprocessor import Tokenizer

    
    for task in get_filenames():
        previous_ids = []
        sourcefile = open(task.filename_source, 'r')
    
        filters = [('source_lang', task.sourcelang), 
                   ('target_lang', task.targetlang)]
        
        tokenizer = Tokenizer(task.sourcelang)
        
        old_id = 0
        for source_sentence in sourcefile:
            old_id += 1
            
            #source_sentence = tokenizer.process_string(source_sentence)
                        
            uid = retrieve_uid(source_sentence, previous_ids, filters)
            if not uid:
                continue
                print "."
            previous_ids.append(uid)
            
            dbentry = [('old_id', old_id), 
                       ('sentence_id', uid),
                       ('source_lang', task.sourcelang),
                       ('target_lang', task.targetlang),
                       ('testset', task.testset),
                       ('system', task.system),
                       ]
            
            dbentries.append(dbentry)
        sourcefile.close()
    db_add_entries(dbentries, 'auto_error_classification')




    
            

if __name__ == '__main__':
    sync_erroclass_ids()
    
    