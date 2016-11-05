'''
Re-implementation of different types of agreements
e.g. for Qtleap Pilot 3
'''
import csv
from collections import defaultdict
import re
import sys
import itertools
from operator import attrgetter


FILEPATTERN = "(..).*Annotator(\d*).*.csv"

def fleiss_kappa(judgment_tuples, annotators_count, categories_count):
    '''
    Fleiss kappa computation of inter-annotator agreement for many annotators_count
    based on: https://gist.github.com/ShinNoNoir/4749548#file-kappa-py-L14
    and on: http://en.wikipedia.org/wiki/Fleiss'_kappa
    
    @param judgment_tuples: list of tuples of item and category values
    @type judgment_tuples: list of tuples
    @param annotators_count: number of annotators_count
    @type annotators_count: number of categories
    @return: kappa score
    @rty        
    '''
    items = set()
    categories = set()
    n_ij = {}
    
    for i, c in judgment_tuples:
        items.add(i)
        categories.add(c)
        n_ij[(i,c)] = n_ij.get((i,c), 0) + 1
    
    items_count = len(items)
    
    p_j = {}
    for c in categories:
        p_j[c] = sum(n_ij.get((i,c), 0) for i in items) / (1.0*annotators_count*items_count)
    
    P_i = {}
    for i in items:
        P_i[i] = (sum(n_ij.get((i,c), 0)**2 for c in categories)-annotators_count) / (annotators_count*(annotators_count-1.0))
    
    #print P_i    
    P_bar = sum(P_i.itervalues()) / (1.0*items_count)
    P_e_bar = sum(p_j[c]**2 for c in categories)
    
    #print "P = ", P_bar
    #print "Pe = ", P_e_bar
    
    kappa = (P_bar - P_e_bar) / (1 - P_e_bar)
    
    return kappa


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
        self.judgments_per_langid_taskid = defaultdict(lambda : defaultdict(list))
        self.judgments_per_taskid = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
        
        # read csv files into the dictionaries
        self.read_csv_files()
        self.calculate_agreement_langid()
        self.calculate_agreement_taskid()
        self.calculate_kappa()
        
    def read_csv_files(self):
        """
        Read all CSV files and store all judgements in the database
        """ 
        for user_filename in self.csv_filenames:
            try:
                langid, uid = re.findall(FILEPATTERN, user_filename).pop()
            except:
                print "error reading filename pattern"
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
                        
                        taskid = taskid.strip()
                        if taskid=='Form4' and score==4:
                            score = 3
                        judgment = Judgment(qid, uid, score, taskid, langid)
                        self.judgments_per_langid[langid][qid][taskid].append(judgment)
                        self.judgments_per_langid_taskid[langid][taskid].append(judgment)
                        self.judgments_per_taskid[taskid][qid][langid].append(judgment)
    
    def calculate_agreement_langid(self):
        for langid in sorted(self.judgments_per_langid.keys()):
            raters, agreement = self.calculate_precision(self.judgments_per_langid[langid])
            print langid, '&', raters, '&', round(agreement, 3), '\\\\'
    
    def calculate_agreement_taskid(self):
        for taskid in sorted(self.judgments_per_taskid.keys()):
            _, agreement = self.calculate_precision(self.judgments_per_taskid[taskid])
            print taskid, '&', round(agreement, 3), '\\\\' 
                
    
    def calculate_kappa(self):
        for langid in sorted(self.judgments_per_langid.keys()):
            judgments = self.judgments_per_langid_taskid[langid]
            for taskid in sorted(judgments.keys()):
                task_judgments = judgments[taskid]
                uids = set()
                categories = set()
                judgment_tuples = []
                for j in task_judgments:
                    judgment_tuples.append((j.qid, j.score))
                    uids.add(j.uid)
                annotators_count = len(uids)
                print langid, taskid, fleiss_kappa(judgment_tuples, annotators_count, len(categories))
                
        #return annotators_count, fleiss_kappa(judgment_tuples, annotators_count, len(categories))
    
    def calculate_precision(self, judgments):
        total = 0
        total_agreed = 0
        judgments_size = []
        uids = set()

        #print "judgments for langid {}".format(len(judgments))
        for _, query_judgments in judgments.iteritems():
            #print "judgments for qid {}: {}".format(qid, len(query_judgments))
            for _, task_judgments in query_judgments.iteritems():
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
    
    
            
            
            
            
        
            
            

        
                        
                
            
            
        
                        