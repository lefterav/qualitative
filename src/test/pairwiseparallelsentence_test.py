'''
@author: lefterav
'''
from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from sentence.pairwisedataset import AnalyticPairwiseDataset, CompactPairwiseDataset, FilteredPairwiseDataset
import os
import unittest
from numpy.ma.testutils import assert_equal
from sentence.rankhandler import RankHandler
from sentence.dataset import DataSet
from io_utils.output.xmlwriter import XmlWriter

class TestPairwiseParallelSentenceConversion(unittest.TestCase):
    """
    Test that the number of sentences stays is the same before and after the conversion
    """
    
    def setUp(self):
        self.filename = "pairwiseparallelsentence_test.jcml"
        self.mydataset = JcmlReader(self.filename).get_dataset()
        
        
    
    def test_dataset_reads_all_parallelsentences(self):
        """
        check if reader reads all the parallelsentences
        """
        ps_len_before = len(self.mydataset.get_parallelsentences())
        f = open(self.filename, 'r')
        f_text = f.read()
        ps_len_after =  f_text.count('<judgedsentence')
        print ps_len_before, ps_len_after
        self.assertEqual(ps_len_before, ps_len_after)    
        f.close()
        
    
    def test_dataset_sizes(self):
        """
        Check whether the same dataset structure gets affected by the conversions
        """
        ps_len_before = len(self.mydataset.get_parallelsentences())
        self.my_pairwise_dataset = AnalyticPairwiseDataset(self.mydataset)
        ps_len_after = len(self.mydataset.get_parallelsentences())
        print ps_len_before, ps_len_after
        self.assertEqual(ps_len_before, ps_len_after)                         
            
    
    def test_sizes_after_pairing(self):
        """
        Check whether the pairwise breakdown of the multiclass sentences has the right size
        """
        
        #how many were there before?
        ps_len_before = len(self.mydataset.get_parallelsentences())
        self.my_pairwise_dataset = AnalyticPairwiseDataset(self.mydataset)
        #how many were there afterwards?
        pss = self.my_pairwise_dataset.get_parallelsentences()
        ps_len_after = len(pss)
    
        #Parallelsentence2Jcml(pss).write_to_file("%s.pairwise" % self.filename)
        
        #how many should there be?
        translation_count_vector = self.mydataset.get_translations_count_vector()
        print translation_count_vector
        pairwise_translation_count_vector = [n*(n-1)/2 for n in translation_count_vector]
        print pairwise_translation_count_vector
        pairwise_translations_altogether = sum(pairwise_translation_count_vector)
        
        print "They are", ps_len_after
        print "They should be", pairwise_translations_altogether
        self.assertEqual(ps_len_after, pairwise_translations_altogether)
    
    
    def test_pairwise_with_both_ways(self):
        pps_new = sorted(AnalyticPairwiseDataset(self.mydataset).get_parallelsentences())
        pps_old = sorted(RankHandler().get_pairwise_from_multiclass_set(self.mydataset.get_parallelsentences(), True, False, False))
        filename1 = "%s.pairnew" % self.filename
        filename2 = "%s.pairold" % self.filename
        Parallelsentence2Jcml(pps_new).write_to_file(filename1)
        Parallelsentence2Jcml(pps_old).write_to_file(filename2)
        self.assertEqual(len(pps_new), len(pps_old))
        self.assertEqual(os.path.getsize(filename1), os.path.getsize(filename2)) 
        
#        self.assertEqual(pps_new, pps_old)
        
        
    def test_ties_removal_from_analytic(self):
        pd_new = AnalyticPairwiseDataset(self.mydataset)
        pd_new.remove_ties()
        pps_new = pd_new.get_parallelsentences()
        pps_old = RankHandler().get_pairwise_from_multiclass_set(self.mydataset.get_parallelsentences(), False, False)
        self.assertEqual(len(pps_new), len(pps_old))


    def test_pairwise_reverse(self):
        pps_original = self.mydataset.get_parallelsentences()
        pps_new = AnalyticPairwiseDataset(self.mydataset).get_parallelsentences()
        pps_rebuilt = RankHandler().get_multiclass_from_pairwise_set(pps_new, True)
        self.assertEqual(len(pps_original), len(pps_rebuilt))
#        self.assertEqual(pps_original, pps_new)
    
    def test_pairwise_merge(self):
        new_analytic = AnalyticPairwiseDataset(self.mydataset)
        new_merged = CompactPairwiseDataset(new_analytic)
        new_merged_sentences = new_merged.get_parallelsentences()
        
        parallelsentences = self.mydataset.get_parallelsentences()
        old_unmerged_sentences = RankHandler().get_pairwise_from_multiclass_set(parallelsentences, True, False, False)
        old_merged_sentences = RankHandler().merge_overlapping_pairwise_set(old_unmerged_sentences) 
    
        filename1 = "%s.mergednew" % self.filename
        filename2 = "%s.mergedold" % self.filename
        Parallelsentence2Jcml(new_merged_sentences).write_to_file(filename1)
        Parallelsentence2Jcml(old_merged_sentences).write_to_file(filename2)
        
        self.assertEqual(len(new_merged_sentences), len(old_merged_sentences), "The two ways of merging differ")
        #self.assertEqual(os.path.getsize(filename1), os.path.getsize(filename2)) 
        
    
#    def test_filter_sentence_28(self):
#        new_analytic = AnalyticPairwiseDataset(self.mydataset)  
#        sentence_id = "28"
#        analytic_parallelsentences = new_analytic.get_parallelsentences()
#        analytic_parallelsentences = [ps for ps in analytic_parallelsentences if ps.get_compact_id() == sentence_id]
#        
#        sentence_ids = set([ps.get_compact_id() for ps in analytic_parallelsentences]) 
#        rank_vector = [tuple(sorted(ps.get_system_names())) for ps in analytic_parallelsentences]
#        rank_pairs = set(rank_vector)
#        
#        new_filtered = FilteredPairwiseDataset(new_analytic, 1.00)
#        
#        print "Should have", unique, "and have" , len(new_filtered_parallelsentences)
#        self.assertEqual(len(new_filtered_parallelsentences), rank_pairs)
#        

    def test_pairwise_28(self):
        sentence_28 = DataSet([ps for ps in self.mydataset.get_parallelsentences() if ps.get_compact_id() == "28"])
        analytic_dataset = AnalyticPairwiseDataset(sentence_28)
        analytic_parallelsentences = analytic_dataset.get_parallelsentences()

        for ps in analytic_parallelsentences:
            rank_items = [(tuple(sorted(ps.get_system_names())), ps.get_rank()) ]
            for rank_item in sorted(rank_items):
                print rank_item
            
        print 
        rank_vector = [tuple(sorted(ps.get_system_names())) for ps in analytic_parallelsentences]
        unique = sorted(set(rank_vector))
        
        #manual check
        self.assertEqual(len(rank_vector), 80)
        self.assertEqual(len(unique), 59)
        
        new_compact = CompactPairwiseDataset(analytic_dataset)
        new_compact_sentences = new_compact.get_parallelsentences()
        self.assertEqual(len(new_compact_sentences), 59)
        new_filtered_sentences = FilteredPairwiseDataset(analytic_dataset, 1.00).get_parallelsentences()
        self.assertEqual(len(new_filtered_sentences), 54)
        new_filtered_sentences = FilteredPairwiseDataset(analytic_dataset, 0.60).get_parallelsentences()
        self.assertEqual(len(new_filtered_sentences), 55)
        
    def test_pairwise_merge_count(self):
        new_analytic = AnalyticPairwiseDataset(self.mydataset)
        analytic_parallelsentences = new_analytic.get_parallelsentences()
        sentence_ids = set([ps.get_compact_id() for ps in analytic_parallelsentences]) 
        print
        unique = 0
        for sentence_id in sentence_ids:
            #get a list of the system name pairs, order irrelevant
            rank_vector = [tuple(sorted(ps.get_system_names())) for ps in analytic_parallelsentences if ps.get_compact_id() == sentence_id]
            
            rank_pairs = set(rank_vector)
        
            print "rank vector for sentence %s has %d comparisons "% (sentence_id, len(rank_vector))
            print "rank vector for sentence %s has %d unique comparisons "% (sentence_id, len(rank_pairs))
            unique += len(rank_pairs)
        
        new_filtered = CompactPairwiseDataset(new_analytic)
        new_filtered_parallelsentences = new_filtered.get_parallelsentences()
        print "Should have", unique, "and have" , len(new_filtered_parallelsentences)
        self.assertEqual(len(new_filtered_parallelsentences), unique)
#        for rank_tupple in rank_vector:
#            print rank_tupple
        filename1 = "%s.filterednew" % self.filename
        Parallelsentence2Jcml(new_filtered_parallelsentences).write_to_file(filename1)
        
        new_filtered = FilteredPairwiseDataset(new_analytic, 0.00)
        new_filtered_parallelsentences = new_filtered.get_parallelsentences()
        print "Should have", unique, "and have" , len(new_filtered_parallelsentences)
        self.assertEqual(len(new_filtered_parallelsentences), unique)
#        for rank_tupple in rank_vector:
#            print rank_tupple
        filename1 = "%s.filterednew" % self.filename
        Parallelsentence2Jcml(new_filtered_parallelsentences).write_to_file(filename1)
        
#class TestPairwiseParallelSentenceConversion(unittest.TestCase):
#
#
##    def setUp(self):
###        path = os.path.abspath(__file__)
##        mydataset = JcmlReader("pairwiseparallelsentence_test.jcml").get_dataset()
##        my_pairwise_dataset = AnalyticPairwiseDataset(mydataset)
##        my_compact_pairwise_dataset = CompactPairwiseDataset(my_pairwise_dataset)
##        
#
#    def tearDown(self):
#        pass
#
#
#    def runTest(self):
#        pass
#
#    def testName(self):
#        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()