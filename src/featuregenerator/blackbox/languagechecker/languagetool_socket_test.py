'''
Created on 14 Mar 2016

@author: elav01
'''
import unittest
from util.jvm import LocalJavaGateway
from languagetool_socket import LanguageToolSocketFeatureGenerator
import logging as log
from numpy.ma.testutils import assert_equal

JAVA = "/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java"

class TestLanguageTool(unittest.TestCase):
    
    def setUp(self):
        log.debug("Loading Java Gateway")
        
        self.gateway = LocalJavaGateway(java=JAVA)
        
        log.debug("Loading language tool")
        self.ltool = LanguageToolSocketFeatureGenerator(lang="en", 
                                                        gateway=self.gateway)        

    def tearDown(self):
        pass

    def testCheckSentence(self):
        string = "These are a very rong Sentence ."
        features = self.ltool.get_features_string(string)
        assert_equal(features, {'lt_issue_whitespace': 1, 'lt_err_COMMA_PARENTHESIS_WHITESPACE_replacements_avgchars': 1.0, 'lt_err_COMMA_PARENTHESIS_WHITESPACE_chars': 2, 'lt_err_COMMA_PARENTHESIS_WHITESPACE_replacements': 1, 'lt_replacements': 2, 'lt_cat_Miscellaneous': 1, 'lt_errors_chars': 2, 'lt_errors': 1, 'lt_err_COMMA_PARENTHESIS_WHITESPACE': 1, 'lt_categories': 1, 'lt_issuetypes': 1})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    
    loglevel = log.DEBUG
    log.basicConfig(level=loglevel,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    unittest.main()