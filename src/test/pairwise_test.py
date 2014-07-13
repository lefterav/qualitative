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
        self.filename = "pairwiseparallelsentence_test.jcml"
        self.mydataset = JcmlReader(self.filename).get_dataset()
    


    def test_pairwise_reconstruct_twice(self):
        """
        Loads a dataset, converts that to pairwise once and reconstructs it. Then it loads that again and reconstructs it once more
        This was helpful to detect a problem of wrong 
        """
        
        
        #first perform typical cleanup of the test set
        analytic_testset = AnalyticPairwiseDataset(self.mydataset) #this 
        filtered_dataset = FilteredPairwiseDataset(analytic_testset, 1.00)
        filtered_dataset.remove_ties()

        output_filename = "filtered_1.jcml"
        Parallelsentence2Jcml(filtered_dataset.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)

        reconstructed_dataset = filtered_dataset.get_multiclass_set()
#        reconstructed_dataset.remove_ties()
        
        output_filename = "reconstructed_1.jcml"
        Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
        #retrieve clean test set from the file and repeat the handling
        simple_testset = JcmlReader(output_filename).get_dataset()
        analytic_testset_2 = AnalyticPairwiseDataset(simple_testset) #this 
        compact_testset_2 = CompactPairwiseDataset(analytic_testset_2)

        output_filename = "filtered_2.jcml"
        Parallelsentence2Jcml(compact_testset_2.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
#        self.assertEqual(len(filtered_dataset.get_parallelsentences()), len(compact_testset_2.get_parallelsentences())) 
        
        reconstructed_dataset_2 = compact_testset_2.get_multiclass_set()
        output_filename = "reconstructed_2.jcml"
        Parallelsentence2Jcml(reconstructed_dataset_2.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
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
        analytic_testset = AnalyticPairwiseDataset(self.mydataset) #this 
        filtered_dataset = FilteredPairwiseDataset(analytic_testset, 1.00)
        filtered_dataset.remove_ties()

        output_filename = "filtered_1.jcml"
        Parallelsentence2Jcml(filtered_dataset.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)

        reconstructed_dataset = filtered_dataset.get_multiclass_set()
#        reconstructed_dataset.remove_ties()
        
        output_filename = "reconstructed_1.jcml"
        Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
        #retrieve pairwise test set from the file and repeat the handling
        simple_testset = JcmlReader("filtered_1.jcml").get_dataset()
        analytic_testset_2 = AnalyticPairwiseDataset(simple_testset) #this 
        compact_testset_2 = CompactPairwiseDataset(analytic_testset_2)

        output_filename = "filtered_2.jcml"
        Parallelsentence2Jcml(compact_testset_2.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
#        self.assertEqual(len(filtered_dataset.get_parallelsentences()), len(compact_testset_2.get_parallelsentences())) 
        
        reconstructed_dataset_2 = compact_testset_2.get_multiclass_set()
        output_filename = "reconstructed_2.jcml"
        Parallelsentence2Jcml(reconstructed_dataset_2.get_parallelsentences(), shuffle_translations=False, sort_attribute="system").write_to_file(output_filename)
        
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