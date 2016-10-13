'''
Re-implementation of different types of agreements
e.g. for Qtleap Pilot 3
'''
import csv
from collections import defaultdict
import re
import sys
import itertools


FILEPATTERN = "(..)Annotator(\d*).csv"

class Judgment:
    def __init__(self, qid, uid, score, taskid, langid):
        self.qid = qid
        self.uid = uid
        self.score = score
        self.taskid = taskid
        self.langid = langid
        
    def __str__(self):
        return "{}:{}:{}:{}".format(self.uid, self.qid, self.langid, self.score)    

class QtLeapJudgementReader:
    
    def __init__(self, csv_filenames):
        self.csv_filenames = csv_filenames
        self.judgments_per_langid = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
        self.judgments_per_taskid = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
        
        # read csv files into the dictionaries
        self.read_csv_files()
        self.calculate_iaaa_langid()
    
        
    def read_csv_files(self):
        """
        Read all CSV files and store all judgements in the database
        """ 
        for user_filename in self.csv_filenames:
            try:
                langid, uid = re.findall(FILEPATTERN, user_filename).pop()
            except:
                print "error"
                continue
            uid = int(uid)
            
            with open(user_filename, 'rb') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',')
                for row in reader:
                    qid = int(row['idQuestion']) 
                    for taskid in row.iterkeys():
                        if taskid == 'idQuestion':
                            continue
                        try:
                            score = int(row[taskid])
                        except:
                            continue
                        
                        if taskid=='Form4' and score==4:
                            score = 3
                        judgment = Judgment(qid, uid, score, taskid, langid)
                        self.judgments_per_langid[langid][qid][taskid].append(judgment)
                        self.judgments_per_taskid[taskid][qid][langid].append(judgment)
    
    def calculate_iaaa_langid(self):
        for langid in sorted(self.judgments_per_langid.keys()):
            #print langid
            raters, agreement = self.calculate_agreement(self.judgments_per_langid[langid])
            print langid, raters, round(agreement, 3) 
        
        
    def calculate_agreement(self, judgments):
        total = 0
        total_agreed = 0
        judgments_size = []
        uids = set()
        #print "judgments for langid {}".format(len(judgments))
        for qid, query_judgments in judgments.iteritems():
            #print "judgments for qid {}: {}".format(qid, len(query_judgments))
            for taskid, task_judgments in query_judgments.iteritems():
                #print "judgments for task_id {}: {}: {}".format(taskid, len(task_judgments), ", ".join([str(j) for j in task_judgments]))
                judgments_size.append(len(task_judgments))
                #print qid, taskid, len(task_judgments)
                for judgment_1, judgment_2 in itertools.combinations(task_judgments, 2):
                    uids.add(judgment_1.uid)
                    uids.add(judgment_2.uid)
                    if judgment_1.uid == judgment_2.uid:
                        continue
                    total+=1
                    if judgment_1.score == judgment_2.score:
                        total_agreed+=1
        return len(uids), total_agreed*1.00/total
            
if __name__ == "__main__":
    filenames = sys.argv[1:]
    calculator = QtLeapJudgementReader(filenames)
    
    
            
            
            
            
        
            
            

        
                        
                
            
            
        
                        