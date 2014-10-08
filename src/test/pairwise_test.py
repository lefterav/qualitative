'''
Created on 14 Jul 2012

@author: Eleftherios Avramidis
'''

from dataprocessor.input.jcmlreader import JcmlReader
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
from sentence.pairwisedataset import AnalyticPairwiseDataset, CompactPairwiseDataset, FilteredPairwiseDataset
import os
import unittest
from numpy.ma.testutils import assert_equal
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from dataprocessor.output.xmlwriter import XmlWriter




class PairwiseTesting(unittest.TestCase):
    '''
    classdocs
    '''
    def setUp(self):
        self.filename = "pairwiseparallelsentence_test.1.jcml"
        self.mydataset = JcmlReader(self.filename).get_dataset()
        self.datasize = 1
        tgt_per_sentence = 3
        self.allpairwise = self.datasize * tgt_per_sentence * (tgt_per_sentence-1) 
        
    def test_sentence_loading(self):
        self.assertEqual(len(self.mydataset.get_parallelsentences()), self.datasize, "Not all sentences read properly")
    
    def test_get_pairwise_parallelsentences_replacement(self):
        pairwise = []
        self.pairsize = 0
        for parallelsentence in self.mydataset.get_parallelsentences():
            pairwise = parallelsentence.get_pairwise_parallelsentences()
            len_translations = len(parallelsentence.get_translations())
            len_pairwise =  len_translations*(len_translations-1)
            self.assertEqual(len(list(pairwise)), len_pairwise, "Amount of pairwise sentences extracted is wrong")
    
    def test_get_pairwise_parallelsentences_noreplacement(self):
        pairwise = []
        self.pairsize = 0
        for parallelsentence in self.mydataset.get_parallelsentences():
            pairwise = parallelsentence.get_pairwise_parallelsentences(replacement=False)
            len_translations = len(parallelsentence.get_translations())
            len_pairwise = 1.00*len_translations*(len_translations-1)/2
            self.assertEqual(len(list(pairwise)), len_pairwise, "Amount of pairwise sentences extracted is wrong")
        
        
    
    def test_create_analytic_replacement(self):
        analytic_testset = AnalyticPairwiseDataset(self.mydataset, replacement=True)
        self.assertEqual(len(analytic_testset.get_parallelsentences()), self.allpairwise, "Amount of pairwize sentences in Analytic Pairwise Set is wrong")

    def test_create_analytic_noreplacement(self):
        analytic_testset = AnalyticPairwiseDataset(self.mydataset, replacement=False)
        self.assertEqual(len(analytic_testset.get_parallelsentences()), self.allpairwise/2,  "Amount of pairwize sentences in Analytic Pairwise Set is wrong")
    
    
    def test_io_order(self):
        #write and read one by one the sentences in a file and check whether what comes back is equal to what went out
        analytic_testset = AnalyticPairwiseDataset(self.mydataset) #this
        output_filename = "analytic_1.jcml"
        
        for initial_parallelsentence in analytic_testset.get_parallelsentences():
            Parallelsentence2Jcml([initial_parallelsentence], shuffle_translations=False).write_to_file(output_filename)
            
            reimported_parallelsentence = JcmlReader(output_filename).get_dataset().get_parallelsentences()[0]
            
            initial_systems = initial_parallelsentence.get_target_attribute_values("system")
            reimported_systems = reimported_parallelsentence.get_target_attribute_values("system")
            
            self.assertEqual(initial_systems, reimported_systems, "One of the pairwise sentences could not be written/read consistently")
        
    
    def test_pairwise_reconstruct_twice(self):
        """
        Loads a dataset, converts that to pairwise once and reconstructs it. Then it loads that again and reconstructs it once more
        This was helpful to detect a problem of wrong 
        """
        analytic_testset = AnalyticPairwiseDataset(self.mydataset) #this
        output_filename = "analytic_1.jcml"
        Parallelsentence2Jcml(analytic_testset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
        
        #first perform typical cleanup of the test set
        analytic_testset = AnalyticPairwiseDataset(self.mydataset) #this
        output_filename = "analytic_1.jcml"
        Parallelsentence2Jcml(analytic_testset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
         
         
        filtered_dataset = FilteredPairwiseDataset(analytic_testset, 1.00)
        #filtered_dataset.remove_ties()

        output_filename = "filtered_1.jcml"
        Parallelsentence2Jcml(filtered_dataset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)

        reconstructed_dataset = filtered_dataset.get_multiclass_set()
#        reconstructed_dataset.remove_ties()
        
        output_filename = "reconstructed_1.jcml"
        Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
        #retrieve clean test set from the file and repeat the handling
        simple_testset = JcmlReader(output_filename).get_dataset()
        analytic_testset_2 = AnalyticPairwiseDataset(simple_testset) #this 
        compact_testset_2 = CompactPairwiseDataset(analytic_testset_2)

        output_filename = "filtered_2.jcml"
        Parallelsentence2Jcml(compact_testset_2.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
#        self.assertEqual(len(filtered_dataset.get_parallelsentences()), len(compact_testset_2.get_parallelsentences())) 
        
        reconstructed_dataset_2 = compact_testset_2.get_multiclass_set()
        output_filename = "reconstructed_2.jcml"
        Parallelsentence2Jcml(reconstructed_dataset_2.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
        reconstructed_1 = reconstructed_dataset.get_parallelsentences()
        reconstructed_2 = reconstructed_dataset_2.get_parallelsentences()
        self.assertEqual(len(reconstructed_1), len(reconstructed_2), "The number of sentences when reconstructing the same set twice has changed")
        
#        for sentence_id in compact_testset_2.get_pairwise_parallelsentence_sets().iterkeys():
#            pset1 = compact_testset_2.get_pairwise_parallelsentence_set(sentence_id)
#            print pset1.get_system_names()
#            pset2 = compact_testset_2.get_pairwise_parallelsentence_set(sentence_id)
#            print pset2.get_system_names()
        
        for p1, p2 in zip(reconstructed_1, reconstructed_2):
            systemrank1 = set([(tgt.get_attribute("system"), tgt.get_attribute("rank")) for tgt in p1.get_translations()]) 
            systemrank2 = set([(tgt.get_attribute("system"), tgt.get_attribute("rank")) for tgt in p2.get_translations()])
            self.assertEqual(systemrank1, systemrank2)
            

    def test_pairwise_save_reconstruct(self):
        """
        Loads a dataset, converts that to pairwise once and reconstructs it. Then it loads that again and reconstructs it once more
        This was helpful to detect a problem of wrong 
        """
        
        
        #first perform typical cleanup of the test set
        analytic_testset = AnalyticPairwiseDataset(self.mydataset, replacement=True) #this 
        filtered_dataset = FilteredPairwiseDataset(analytic_testset, 1.00)
        filtered_dataset.remove_ties()

        output_filename = "filtered_1.jcml"
        Parallelsentence2Jcml(filtered_dataset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)

        reconstructed_dataset = filtered_dataset.get_multiclass_set()
#        reconstructed_dataset.remove_ties()
        
        output_filename = "reconstructed_1.jcml"
        Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
        #retrieve pairwise test set from the file and repeat the handling
        simple_testset = JcmlReader("filtered_1.jcml").get_dataset()
        analytic_testset_2 = AnalyticPairwiseDataset(simple_testset) #this 
        compact_testset_2 = CompactPairwiseDataset(analytic_testset_2)

        output_filename = "filtered_2.jcml"
        Parallelsentence2Jcml(compact_testset_2.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
#        self.assertEqual(len(filtered_dataset.get_parallelsentences()), len(compact_testset_2.get_parallelsentences())) 
        
        reconstructed_dataset_2 = compact_testset_2.get_multiclass_set()
        output_filename = "reconstructed_2.jcml"
        Parallelsentence2Jcml(reconstructed_dataset_2.get_parallelsentences(), shuffle_translations=False).write_to_file(output_filename)
        
        reconstructed_1 = reconstructed_dataset.get_parallelsentences()
        reconstructed_2 = reconstructed_dataset_2.get_parallelsentences()
        self.assertEqual(len(reconstructed_1), len(reconstructed_2), "The number of sentences when reconstructing the same set twice has changed")
        
#        for sentence_id in compact_testset_2.get_pairwise_parallelsentence_sets().iterkeys():
#            pset1 = compact_testset_2.get_pairwise_parallelsentence_set(sentence_id)
#            print pset1.get_system_names()
#            pset2 = compact_testset_2.get_pairwise_parallelsentence_set(sentence_id)
#            print pset2.get_system_names()
        
        for p1, p2 in zip(reconstructed_1, reconstructed_2):
            systemrank1 = set([(tgt.get_attribute("system"), tgt.get_attribute("rank")) for tgt in p1.get_translations()]) 
            systemrank2 = set([(tgt.get_attribute("system"), tgt.get_attribute("rank")) for tgt in p2.get_translations()])
            self.assertEqual(systemrank1, systemrank2)


#        rank_vector_1
        
        
#        equal_sentences(reconstructed_dataset_2, reconstructed_dataset)
        
        #first see if number of sentences at the compact sets are equal