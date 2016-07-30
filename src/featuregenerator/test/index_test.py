'''
Created on Jul 28, 2016

@author: lefterav
'''
from __future__ import absolute_import
import unittest
from featuregenerator.index import FeatureGeneratorManager
from featuregenerator.blackbox.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator
from featuregenerator.blackbox.parser.bitpar import BitParserFeatureGenerator
from featuregenerator.blackbox.ibm1 import AlignmentFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgRulesExtractor
from featuregenerator.blackbox.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.blackbox.lm.server import ServerNgramFeatureGenerator


class Test(unittest.TestCase):

    def test_get_feature_generators(self):
        fmg = FeatureGeneratorManager()

        feature_set = ['berkeley-n','bit_avgprob','bit_minprob','bit_prob','bit_stdprob']
        generators = fmg.get_feature_generators(feature_set)
        self.assertEqual(generators, [BerkeleyFeatureGenerator, BitParserFeatureGenerator], "The feature generators selected are not correct.")
        
        feature_set = ['cfgal_count_NP_NP','cfgpos_end_S-VP','cfgpos_end_VP-VP','cross-bleu','cross-meteor_fragPenalty',
                       'cross-meteor_score','ibm1-ratio-001','ibm1-ratio-02','ibm1-score','ibm1-score-inv','l_avgchars',
                       'l_avgoccurences','l_tokens','lm_prob','lm_unk','lm_unk_len','lm_unk_pos_abs_avg','lm_unk_pos_abs_max',
                       'lm_unk_pos_abs_min','lm_unk_pos_rel_avg','lm_unk_pos_rel_max','lm_unk_pos_rel_std',
                       'lt_COMMA_PARENTHESIS_WHITESPACE','lt_UPPERCASE_SENTENCE_START','lt_errors','parse-NN','parse-NN-pos-avg',
                       'parse-NP','parse-NP-pos-std','parse-PP','parse-PP-pos-std','parse-VP','parse-VP-pos-std','parse-comma',
                       'parse-comma-pos-avg','parse-comma-pos-std','parse-dot','parse_VP_height_avg','parse_VP_height_max',
                       'q_1002_1','q_1003_1','q_1004_1','q_1012_1','q_1013_1','q_1015_1','q_1064_1','q_1079_1','q_1081_1','q_1082_1']
        generators = fmg.get_feature_generators(feature_set)
        print generators
        shouldbe = [BerkeleyFeatureGenerator, CfgRulesExtractor, AlignmentFeatureGenerator, ServerNgramFeatureGenerator, LanguageToolSocketFeatureGenerator, ParserMatches]
        self.assertEqual(generators, shouldbe, "The feature generators selected are not correct.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_feature_generators']
    unittest.main()