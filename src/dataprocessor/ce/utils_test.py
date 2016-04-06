'''
Created on Mar 27, 2016

@author: lefterav
'''
import unittest
import os
from utils import fold_jcml_respect_ids
from cejcml import CEJcmlReader
from numpy.ma.testutils import assert_equal

class Test(unittest.TestCase):


    def setUp(self):
        self.filename = "/tmp/test_entire.jcml"
        strings = ['<?xml version="1.0" encoding="utf-8"?>\n<jcml>']
        for s in range(5):
            for i in range(5):
                for _ in range(i*10):
                    strings.append("  <judgedsentence langsrc='de' langtgt='en' testset='{}' id='{}' />".format(s, i))
        strings.append("</jcml>")
        f = open(self.filename, 'w')
        f.write("\n".join(strings))
        f.close()

    def tearDown(self):
        os.unlink(self.filename)


    def test_fold_fold_jcml_respect_ids(self):
        train_filename = "/tmp/test_train.jcml"
        test_filename = "/tmp/test_test.jcml"
        repetitions = 5
        for fold in range(5):
            fold_jcml_respect_ids(self.filename, train_filename, 
                                  test_filename, repetitions, fold)
            all_ids = [p.get_compact_id() for p in CEJcmlReader(self.filename, all_general=True, all_target=True)]
            train_ids = [p.get_compact_id() for p in CEJcmlReader(train_filename, all_general=True, all_target=True)]
            test_ids = [p.get_compact_id() for p in CEJcmlReader(test_filename, all_general=True, all_target=True)]
            # Make sure ids of training and test set do not overlap
            
            count_all = len(all_ids)
            count_train = len(train_ids)
            count_test = len(test_ids)
            assert_equal(count_all, count_train + count_test, 
                         "Fold {}: Joining the split sets does not yield as many sentences as the original set had".format(fold))
            assert_equal(count_train > count_test, True, 
                         "Fold {}".format("Training set is not bigger than test set"))
            
            all_ids = set(all_ids)
            train_ids = set(train_ids)
            test_ids = set(test_ids)
            assert_equal(test_ids.intersection(train_ids), set([]),
                         "Fold {}: There is overlap between training and test set:".format(fold))
            # Make sure sum ids of training and test set equal the total ids   
            assert_equal(all_ids, train_ids.union(test_ids), 
                         "Fold {}: Not all ids of the original set exist in split sets".format(fold))
            #os.unlink(test_filename)
            #os.unlink(train_filename)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()