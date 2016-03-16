'''
Created on 14 Mar 2016

@author: elav01
'''
import unittest
from util.jvm import LocalJavaGateway
import os
from berkeleyparsersocket import BerkeleyParserSocket
from numpy.ma.testutils import assert_equal

GRAMMAR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 
                          '..', '..', '..', '..', '..', '..', 
                          'res', 'grammars', 'eng_sm6.gr'))

class TestBerkeleyParserSocket(unittest.TestCase):

    def setUp(self):
        self.gateway = LocalJavaGateway()
        self.parser = BerkeleyParserSocket(GRAMMAR, self.gateway)

    def tearDown(self):
        self.gateway.shutdown()

    def testParse(self):
        sentence = self.parser.parse("This is a test")
        assert(len(sentence["nbest"]) > 0, "Parser should return at list one result")
        assert_equal(sentence["nbest"][0]["tree"], '(S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test)))) )')
        assert_equal(sentence["nbest"][0]["confidence"], u'-26.320426032971984')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()