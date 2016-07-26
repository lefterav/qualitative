'''
Created on 27 Feb 2012

@author: Eleftherios Avramidis
'''
import unittest
from dataprocessor.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml


class CoupledDataSetTest(unittest.TestCase):

    def setUp(self):
        self.input_file = "/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training-sample.jcml"
        self.output_file = "/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training-sample.coupled.jcml"
        self.simple_dataset = JcmlReader(self.input_file).get_dataset()
        self.coupled_dataset = CoupledDataSet(construct = self.simple_dataset)
        

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
    
    def test_ondisk_vs_onmemory(self):
        pass
#        Parallelsentence2Jcml(self.coupled_dataset.get_parallelsentences()).write_to_file(self.output_file.replace("jcml", "memory.jcml"))
#        coupledfile_disk = self.output_file.replace("jcml", "disk.jcml")
#        coupledfile_memory = self.output_file.replace("jcml", "memory.jcml")
#        CoupledDataSetDisk(self.simple_dataset).write(coupledfile_disk)
#        coupled_dataset = CoupledDataSet(readfile = coupledfile_disk)
#        Parallelsentence2Jcml(self.coupled_dataset).write_to_file(coupledfile_memory)
#        self.assertEqual(self.coupled_dataset, coupled_dataset)
        
                                                                                                                 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()