'''
Created on 26 Feb 2016

@author: elav01
'''
import unittest
import logging
from evaluation.ranking.set import kendall_tau_set
from evaluation.ranking.segment import Ranking

class KendallTauSetTests(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_perfect_tau_correlation(self):
        ranking1 = [1, 2, 3, 4, 5]
        ranking2 = [1, 2, 3, 4] 
        ranking3 = [1, 2, 3, 4, 5, 6, 7]
        set1 = [Ranking(ranking1), Ranking(ranking2), Ranking(ranking3)]
        stats = kendall_tau_set(set1, set1)
        self.assertAlmostEqual(stats["tau"], 1)        
        
    def test_negative_tau_correlation(self):
        ranking1 = [1, 2, 3, 4, 5]
        ranking2 = [1, 2, 3, 4] 
        ranking3 = [1, 2, 3, 4, 5, 6, 7]
        set1 = [Ranking(ranking1), Ranking(ranking2), Ranking(ranking3)]
        set3 = [Ranking(reversed(ranking1)), 
                Ranking(reversed(ranking2)), 
                Ranking(reversed(ranking3))]
        stats = kendall_tau_set(set1, set3)
        self.assertAlmostEqual(stats["tau"], -1)
        
    def test_zero_tau_correlation(self):
        ranking1_1 = Ranking([1, 2, 3, 4, 5, 6])
        ranking1_2 = Ranking([1, 2, 3, 4]) 
        set1 = [ranking1_1, ranking1_2]
        
        ranking2_1 = Ranking([3, 3, 3, 3, 3, 3])
        ranking2_2 = Ranking([4, 4, 4, 4]) 
        set2 = [ranking2_1, ranking2_2]
        
        stats = kendall_tau_set(set2, set1, penalize_predicted_ties=False)
        self.assertAlmostEqual(stats["tau"], 0)
        stats = kendall_tau_set(set1, set2, penalize_predicted_ties=False)
        self.assertAlmostEqual(stats["tau"], 0)
    
    def test_zero_tau_probability(self):
        ranking1_1 = Ranking([1, 2, 3, 4, 5, 6])
        ranking1_2 = Ranking([1, 2, 3, 4]) 
        set1 = [ranking1_1, ranking1_2]
        
        stats = kendall_tau_set(set1, set1)
        self.assertAlmostEqual(stats["tau_prob"], 0)
        self.assertAlmostEqual(stats["tau_weighed_prob"], 0, places=2)
        self.assertAlmostEqual(stats["tau_invw_std"], 0, places=4)
        self.assertAlmostEqual(stats["tau_pooled_std"], 0)
        
    def test_various_tau_probabilities(self):
        set1 = [Ranking([1, 2, 3, 4, 5, 6]),
               Ranking([5, 4, 3, 2, 1]),
               Ranking([2, 2, 2, 1, 3]),
               Ranking([1, 2, 3, 5, 4])
               ]
        set2 = [Ranking([1, 2, 3, 4, 6, 5]),
               Ranking([5, 4, 3, 1, 2]),
               Ranking([2, 2, 2, 3, 1]),
               Ranking([1, 2, 3, 4, 5])
               ]
        stats = kendall_tau_set(set1, set2)
        logging.info("Stats : {}".format(stats))

        
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']\
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
    logging.debug("Test")
    unittest.main()
    