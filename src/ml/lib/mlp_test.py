'''
Created on Apr 7, 2016

@author: lefterav
'''

from ml.lib.mlp import ListNetRanker, dataset_to_instances
from dataprocessor.jcml.writer import IncrementalJcml
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence

import numpy as np
from numpy.testing.utils import assert_equal
from numpy.ma.testutils import assert_array_almost_equal
import os
import tempfile
import unittest
from mlproblems.generic import MLProblem
from sentence.ranking import Ranking

class MLpTest(unittest.TestCase):


    def setUp(self):
        #create a temporary file and populate it with some ranks
        self.train_filename = os.path.join(tempfile.gettempdir(), "MLpTrain.jcml")
        self.test_filename = os.path.join(tempfile.gettempdir(), "MLpTest.jcml")
        self._create_dataset(100, self.train_filename)        

        
    def _create_dataset(self, items, filename, default_rank = [1, 2, 3, 4, 5]):   
        writer = IncrementalJcml(filename)
        
        for i in range(items):
            translations = []
            for j in range(5):
                attributes = dict([("att_{}".format(k), k+j) for k in range(20)])
                #attributes["rank_strings"] = j
                attributes["rank_strings"] = default_rank[j]
                translation = SimpleSentence("", attributes)
                translations.append(translation)
            source = SimpleSentence("", {})
            parallelsentence = ParallelSentence(source, translations, source, 
                                                {'langsrc':'de', 
                                                 'langtgt':'en', 
                                                 'testset':'test',
                                                 'id': i })
            writer.add_parallelsentence(parallelsentence)
        writer.close()     

    def tearDown(self):
        #delete the temp file
        os.unlink(self.train_filename)

    def test_dataset_to_instances(self, default_rank = [1, 2, 3, 4, 5]):
        #create the final numpy array manually and see if the conversion happens ok
        newdata = []
        default_rank = Ranking(default_rank).inverse().integers()
        for i in range(1, 101):
            for rank_strings in range(5):
                vector = sorted([(str(k),k+rank_strings) for k in range(20)])
                vector = np.array([float(v) for _, v in vector])
                #newdata.append([vector, int(rank_strings)+1, i])
                newdata.append([vector, default_rank[rank_strings], i])
        newdata = np.array(newdata)
        newmetadata = {'input_size' : 20, #size of feature vector
                       'scores' :  set([1, 2, 3, 4, 5])}
        
        data, metadata = dataset_to_instances(self.train_filename).raw_source()
        for i in range(np.shape(data)[0]):
            vector1, rank1, query1 = data[i]
            vector2, rank2, query2 = newdata[i]
            assert_array_almost_equal(vector1, vector2, err_msg="MLPython: error in the conversion of batch data")
            assert_equal(rank1, rank2, err_msg="MLPython: error in the conversion of rank_strings value")
            assert_equal(query1, query2)
        assert_equal(metadata, newmetadata, err_msg="MLPython: error in the conversion of metadata")

    def _create_single_instance(self):
        for rank_strings in range(5):
            vector = sorted([(str(k),k+rank_strings) for k in range(20)])
            data = np.array([float(v) for _, v in vector])
            
        metadata = {'input_size' : 20, #size of feature vector
                    'scores' :  set([1, 2, 3, 4, 5])}
        return MLProblem(data, metadata)
            
    def test_listnet_train(self):
        learner = ListNetRanker()
        learner.train(self.train_filename, class_name="rank_strings")
        
        self._create_dataset(1, self.test_filename)
        print "Result: "
        print learner.test(self.test_filename, "/tmp/testoutput.jcml")
        os.unlink(self.test_filename)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    