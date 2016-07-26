'''
Created on Mar 16, 2016

@author: lefterav
'''
import unittest
from featuregenerator.blackbox.lm.ken import KenLMFeatureGenerator


class TestKenLM(unittest.TestCase):

    def setUp(self):
        filename = '/home/lefterav/Research/sandbox/wmt16/libreoffice-help.binlm.2'
        self.lm = KenLMFeatureGenerator('de', 5, filename)
        
    def tearDown(self):
        print self.lm.get_features_string("das ist ein sehr gute Nachricht")

    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()