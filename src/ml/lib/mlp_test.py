'''
Created on Apr 7, 2016

@author: lefterav
'''

from __future__ import absolute_import
import unittest
from ml.lib.mlp import ListNet  
from dataprocessor.sax.saxps2jcml import IncrementalJcml
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
import os

class Test(unittest.TestCase):


    def setUp(self):
        self.tmpfilename = "/tmp/tssasdasd.jcml"
        writer = IncrementalJcml(self.tmpfilename)
        for i in range(100):
            translations = []
            for j in range(5):
                attributes = dict([("att_{}".format(k), k+j) for k in range(20)])
                attributes["rank"] = j
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
        #os.unlink(self.tmpfilename)
        pass


    def test_listnet_train(self):
        model = ListNet()
        model.train(self.tmpfilename, class_name="rank")
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()