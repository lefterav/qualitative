'''
Created on 14 Mar 2016

@author: elav01
'''
import unittest
from util.jvm import LocalJavaGateway
from languagetool_socket import LanguageToolSocketFeatureGenerator

JAVA = "/home/elav01/tools/jdk1.8.0_72/bin/java"

class Test(unittest.TestCase):
    
    def setUp(self):
        self.gateway = LocalJavaGateway(java=JAVA)
        self.ltool = LanguageToolSocketFeatureGenerator(lang="en", 
                                                        gateway=self.gateway)        

    def tearDown(self):
        pass

    def testName(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()