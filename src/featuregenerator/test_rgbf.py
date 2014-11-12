'''
Created on 12 Nov 2014

@author: Eelftherios Avramidis
'''
import unittest
from rgbf import RgbfGenerator


class Test(unittest.TestCase):


    def setUp(self):
        self.scorer = RgbfGenerator()
        self.refunits = "This time the fall in stocks on Wall Street is responsible for the drop . ++ This time the fall in stock on Wall Street be responsible for the drop . ++ Th is time the fall in stock s on Wall Street is responsible for the drop .  ++ DT NN DT NN IN NNS IN NP NP VBZ JJ IN DT NN SENT".split("++")
        self.hypunits = "This time , the reason for the collapse on Wall Street . ++ This time , the reason for the collapse on Wall Street . ++ Th is time , the reason for the collapse on Wall Street .  ++ DT NN , DT NN IN DT NN IN NP NP SENT".split("++")

    def test_scoreExampleSentence(self):
        result = self.scorer.process_string_multiunit(self.hypunits, [self.refunits])
        
        correct_result = {'u1-1gram-F': 66.6666666667,
        'u1-1gram-Prec': 75.0,
        'u1-1gram-Rec': 60.0,
        'u1-2gram-F': 32.0,
        'u1-2gram-Prec': 36.3636363636,
        'u1-2gram-Rec': 28.5714285714,
        'u1-3gram-F': 8.69565217391,
        'u1-3gram-Prec': 10.0,
        'u1-3gram-Rec': 7.69230769231,
        'u1-4gram-F': 0.0,
        'u1-4gram-Prec': 0.0,
        'u1-4gram-Rec': 0.0,
        'rgbF': 26.8405797101,
        'rgbPrec': 30.3409090909,
        'rgbRec': 24.0659340659}
        
        for key, found_value in result.iteritems():
            correct_value = correct_result[key]
            self.assertAlmostEqual(correct_value, found_value, places=7, msg="RgbF script does not provide correct result for {}".format(key))
    
        
        


if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.scoreExampleSentence']
    unittest.main()