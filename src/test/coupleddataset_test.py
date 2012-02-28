'''
Created on 27 Feb 2012

@author: lefterav
'''
import unittest
from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet
from io.sax.saxps2jcml import Parallelsentence2Jcml


class CoupledDataSetTest(unittest.TestCase):

    def setUp(self):
        self.input_file = "/home/lefterav/taraxu_data/wmt12/qe/training_set_sample/training.jcml"
        self.output_file = "/home/lefterav/taraxu_data/wmt12/qe/training_set_sample/training.coupled.jcml"
        self.simple_dataset = JcmlReader(self.input_file).get_dataset()
        self.coupled_dataset = CoupledDataSet(self.simple_dataset)
        

    def test_coupling(self):
        coupled_parallelsentences = self.coupled_dataset.get_parallelsentences()
        n = len(self.simple_dataset.get_parallelsentences())
        m = len(coupled_parallelsentences)
        self.assertEqual(m, n*(n-1)/2, "The number of the couples generated is not the proper one")
        Parallelsentence2Jcml(coupled_parallelsentences).write_to_file(self.output_file)
        
    def test_decoupling(self):
        decoupled_dataset = self.coupled_dataset.get_single_set()
        n = len(self.simple_dataset.get_parallelsentences())
        m = len(decoupled_dataset.get_parallelsentences())
        self.assertEqual(m, n, "Coupling and decoupling doesn't regenerate same number of sentences as in input")
        Parallelsentence2Jcml(decoupled_dataset.get_parallelsentences()).write_to_file(self.output_file.replace("jcml", "decoupled.jcml"))
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()