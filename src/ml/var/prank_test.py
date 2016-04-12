'''
Created on Mar 23, 2016

@author: lefterav
'''
import unittest
import numpy as np
from prank import PRank
from numpy.ma.testutils import assert_equal

class PRankTest(unittest.TestCase):


    def testTrainTest(self):
        traindata = np.array([[1, 1, 1, 1, 1],
                          [0.5, 1, 2, 1, 3],
                          [1, 1, 1, 0, 0],
                          [1, 1, 0, 0, 0],
                          ])
    
        labels = np.array([[0,2,3,4,5],
                           [1,2,3,4,5],
                           [2,2,3,4,5],
                           [3,1,1,5,2],                 
                          ])
        
        k = len(set(labels[:,0]))
        ranker = PRank(k)
        ranker.train(traindata, labels)
        testdata = np.array([1.1, 1, 0, 0, 1])
        print ranker.rank(testdata)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()