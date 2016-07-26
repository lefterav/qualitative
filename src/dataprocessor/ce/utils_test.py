'''
Created on Mar 27, 2016

@author: lefterav
'''
import unittest
import os
from utils import fold_jcml_respect_ids
from cejcml import CEJcmlReader
from sentence.dataset import DataSet
from sentence.parallelsentence import ParallelSentence
from dataprocessor.ce.utils import fold_respect_ids
from sentence.sentence import SimpleSentence
import logging as log
from random import randint

class Test(unittest.TestCase):


    def setUp(self):
        pass
        
    def tearDown(self):
        pass


#     def test_fold_respect_ids(self):
#         repetitions = 5
#         dataset = DataSet()
#         for s in range(5):
#             for i in range(2):
#                 for _ in range(2):
#                     attributes = {'langsrc': 'de',
#                                   'langtgt': 'en',
#                                   'testset': s,
#                                   'id': i}
#                     translations = []
#                     for j in range(3):
#                         translations.append(SimpleSentence("string", {"system" : str(j), "rank" : 4-j }))
#                     parallelsentence = ParallelSentence(source="", 
#                                                         translations=translations, 
#                                                         reference="", 
#                                                         attributes=attributes)
#                     dataset.add_parallelsentence(parallelsentence)
#         log.info("{} sentences created artificially".format(len(dataset)))
#          
#         for fold in range(repetitions):
#             training_dataset = DataSet()
#             test_dataset = DataSet()
#             fold_respect_ids(dataset, training_dataset, test_dataset, repetitions, fold)
#             all_ids = [p.get_fileid_tuple() for p in dataset]
#             train_ids = [p.get_fileid_tuple() for p in training_dataset]
#             test_ids = [p.get_fileid_tuple() for p in test_dataset]
#             # Make sure ids of training and test set do not overlap
#              
#             count_all = len(all_ids)
#             count_train = len(train_ids)
#             count_test = len(test_ids)
#             self.assertEqual(count_all, count_train + count_test, 
#                          "Fold {}: Joining the split sets does not yield as many sentences as the original set had".format(fold))
#             self.assertEqual(count_train > count_test, True, 
#                          "Fold {}".format("Training set is not bigger than test set"))
#              
#             all_ids = set(all_ids)
#             train_ids = set(train_ids)
#             test_ids = set(test_ids)
#             self.assertEqual(test_ids.intersection(train_ids), set([]),
#                          "Fold {}: There is overlap between training and test set:".format(fold))
#             # Make sure sum ids of training and test set equal the total ids   
#             self.assertEqual(all_ids, train_ids.union(test_ids), 
#                          "Fold {}: Not all ids of the original set exist in split sets".format(fold))

    def test_fold_jcml_respect_ids(self):
         
        filename = "/tmp/test_entire.jcml"
        strings = ['<?xml version="1.0" encoding="utf-8"?>\n<jcml>']
        repetitions = 5
        
        sentences_per_id = 2
 
        for s in range(1, repetitions+1):
            for i in range(1, sentences_per_id+1):
                for _ in range(1, i*3+1):
                    strings.append("  <judgedsentence langsrc='de' langtgt='en' testset='{}' id='{}'>".format(s, i))
                    for j in range(1,4):
                        strings.append("  <tgt system='{}' rank='{}'> </tgt>".format(randint(1,20), 4-j))
                    strings.append("  </judgedsentence>".format(s, i))
        strings.append("</jcml>")
        f = open(filename, 'w')
        f.write("\n".join(strings))
        f.close()
         
        train_filename = "/tmp/test_train.jcml"
        test_filename = "/tmp/test_test.jcml"
        for fold in range(repetitions):
            fold_jcml_respect_ids(filename, train_filename, test_filename, repetitions, fold, clean_testset=False)
            all_ids = [p.get_fileid_tuple() for p in CEJcmlReader(filename, all_general=True, all_target=True)]
            train_ids = [p.get_fileid_tuple() for p in CEJcmlReader(train_filename, all_general=True, all_target=True)]
            test_ids = [p.get_fileid_tuple() for p in CEJcmlReader(test_filename, all_general=True, all_target=True)]
            # Make sure ids of training and test set do not overlap
             
            count_all = len(all_ids)
            count_train = len(train_ids)
            count_test = len(test_ids)
            self.assertEqual(count_all, count_train + count_test, 
                         "Fold {}: Joining the split sets does not yield as many sentences as the original set had".format(fold))
            self.assertGreater(count_train, count_test, 
                         "Fold {}".format("Training set is not bigger than test set: {} < {}".format(count_train, count_test)))
             
            all_ids = set(all_ids)
            train_ids = set(train_ids)
            test_ids = set(test_ids)
            self.assertEqual(test_ids.intersection(train_ids), set([]),
                         "Fold {}: There is overlap between training and test set:".format(fold))
            # Make sure sum ids of training and test set equal the total ids   
            self.assertEqual(all_ids, train_ids.union(test_ids), 
                         "Fold {}: Not all ids of the original set exist in split sets".format(fold))
            
            counter = 0
            reorder = 0
            for p in CEJcmlReader(test_filename, all_general=True, all_target=True):
                counter+=1
                ranking = p.get_ranking()
                if (ranking.normalize() == range(1, len(ranking)+1)):
                    reorder += 1
            self.assertNotEqual(reorder, counter, "Ranking has been systematically reordered")
            
            fold_jcml_respect_ids(filename, train_filename, test_filename, repetitions, fold, clean_testset=True)
            test_length = len(CEJcmlReader(test_filename, all_general=True, all_target=True))
            
            self.assertEqual(test_length, sentences_per_id, "Testset cleanup did not happen properly: {}".format(test_length))
            
            counter = 0
            reorder = 0
            for p in CEJcmlReader(test_filename, all_general=True, all_target=True):
                counter+=1
                ranking = p.get_ranking()
                if (ranking.normalize() == range(1, len(ranking)+1)):
                    reorder += 1
            self.assertNotEqual(reorder, counter, "Ranking has been systematically reordered")
            
        os.unlink(test_filename)
        os.unlink(train_filename)
        os.unlink(filename)

if __name__ == "__main__":
#    import sys;sys.argv = ['', 'Test.testName']
    #loglevel = log.DEBUG
#     log.basicConfig(level=loglevel,
#                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#                     datefmt='%m-%d %H:%M')
    unittest.main()