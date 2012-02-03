'''
@author: lefterav
'''
from io.input.jcmlreader import JcmlReader
from sentence.pairwisedataset import AnalyticPairwiseDataset, CompactPairwiseDataset
import os
import unittest

class TestPairwiseParallelSentenceConversion(unittest.TestCase):


    def setUp(self):
#        path = os.path.abspath(__file__)
        mydataset = JcmlReader("pairwiseparallelsentence_test.jcml").get_dataset()
        my_pairwise_dataset = AnalyticPairwiseDataset(mydataset)
        my_compact_pairwise_dataset = CompactPairwiseDataset(my_pairwise_dataset)
        

    def tearDown(self):
        pass


    def runTest(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()