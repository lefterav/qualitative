'''
Created on 14 Mar 2016

@author: elav01
'''
import unittest
from util.jvm import LocalJavaGateway
from languagetool_socket import LanguageToolSocketFeatureGenerator
import logging as log

JAVA = "java"

class TestLanguageTOol(unittest.TestCase):
    
    def setUp(self):
        log.info("Loading Java Gateway")
        
        self.gateway = LocalJavaGateway(java=JAVA)
        
        log.info("Loading language tool")
        self.ltool = LanguageToolSocketFeatureGenerator(lang="en", 
                                                        gateway=self.gateway)        

    def tearDown(self):
        pass

    def testName(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    
    loglevel = log.DEBUG
    log.basicConfig(level=loglevel,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    unittest.main()