'''
Created on Jul 28, 2016

@author: lefterav
'''
from __future__ import absolute_import
import unittest
from featuregenerator.index import FeatureGeneratorManager
from featuregenerator.blackbox.parser.berkeley.berkeleyclient import BerkeleyLocalFeatureGenerator
from featuregenerator.blackbox.parser.bitpar import BitParFeatureGenerator
from featuregenerator.blackbox.ibm1 import Ibm1FeatureGenerator
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgRulesExtractor
from featuregenerator.blackbox.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.blackbox.lm.server import ServerNgramFeatureGenerator
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator
from ConfigParser import RawConfigParser
from util.jvm import LocalJavaGateway
import os
from featuregenerator.blackbox.lm.ken import KenLMFeatureGenerator


class Test(unittest.TestCase):

    def test_get_feature_generators(self):
        manager = FeatureGeneratorManager()

        feature_set = ['berkeley-n','bit_avgprob','bit_minprob','bit_prob','bit_stdprob']
        generators = set(manager.get_feature_generators(feature_set))
        shouldbe = set([BerkeleyLocalFeatureGenerator, BitParFeatureGenerator])
        self.assertEqual(generators, shouldbe, 
                         "The feature generators selected are not correct. \n obtained: {}, \n should be: {}".format([g.__name__ for g in generators], [g.__name__ for g in shouldbe]))
        
        feature_set = ['cfgal_count_NP_NP','cfgpos_end_S-VP','cfgpos_end_VP-VP','cross-bleu','cross-meteor_fragPenalty',
                       'cross-meteor_score','ibm1-ratio-001','ibm1-ratio-02','ibm1-score','ibm1-score-inv','l_avgchars',
                       'l_avgoccurences','l_tokens','lm_prob','lm_unk','lm_unk_len','lm_unk_pos_abs_avg','lm_unk_pos_abs_max',
                       'lm_unk_pos_abs_min','lm_unk_pos_rel_avg','lm_unk_pos_rel_max','lm_unk_pos_rel_std',
                       'lt_COMMA_PARENTHESIS_WHITESPACE','lt_UPPERCASE_SENTENCE_START','lt_errors','parse-NN','parse-NN-pos-avg',
                       'parse-NP','parse-NP-pos-std','parse-PP','parse-PP-pos-std','parse-VP','parse-VP-pos-std','parse-comma',
                       'parse-comma-pos-avg','parse-comma-pos-std','parse-dot','parse_VP_height_avg','parse_VP_height_max',
                       'q_1002_1','q_1003_1','q_1004_1','q_1012_1','q_1013_1','q_1015_1','q_1064_1','q_1079_1','q_1081_1','q_1082_1']
        generators = set(manager.get_feature_generators(feature_set))

        shouldbe = set([BerkeleyLocalFeatureGenerator, CfgRulesExtractor, CrossMeteorGenerator, Ibm1FeatureGenerator, ServerNgramFeatureGenerator, LanguageToolSocketFeatureGenerator, ParserMatches])
        self.assertEqual(generators, shouldbe, 
                         "The feature generators selected are not correct. \n obtained: {}, \n should be: {}".format([g.__name__ for g in generators], [g.__name__ for g in shouldbe]))
        
    def test_load_feature_generators(self):
        #generators = [BerkeleyLocalFeatureGenerator, CfgRulesExtractor, KenLMFeatureGenerator, ]
        generators = [CrossMeteorGenerator, ParserMatches, LanguageToolSocketFeatureGenerator]
        manager = FeatureGeneratorManager()
        
        config = RawConfigParser()

        source_language = "en"
        target_language = "de"
        
        gateway = LocalJavaGateway()
        
        initialized = manager.initialize_given_feature_generators(generators, config, source_language, target_language, gateway)
        self.assertEqual(len(initialized), 6)
    
    def test_load_berkeley_generator(self):
        generators = [BerkeleyLocalFeatureGenerator]
        
        manager = FeatureGeneratorManager()
        
        config = RawConfigParser()
        source_language = "en"
        target_language = "de"
        config.add_section("BerkeleyLocal:en")
        config.set("BerkeleyLocal:en", "grammarfile", os.path.abspath("../../../res/grammars/eng_sm6.gr"))
        
        config.add_section("BerkeleyLocal:de")
        config.set("BerkeleyLocal:de", "grammarfile", os.path.abspath("../../../res/grammars/ger_sm5.gr"))
        
        gateway = LocalJavaGateway()
        
        initialized = manager.initialize_given_feature_generators(generators, config, source_language, target_language, gateway)
        self.assertEqual(len(initialized), 2)
        
    def test_load_bilingual_generators(self):
        generators = [Ibm1FeatureGenerator]
        config = RawConfigParser()
        config.add_section("Ibm1:de-en")
        config.set("Ibm1:de-en", "model", os.path.abspath("../../../res/ibm1/lex.de-en"))
        config.add_section("Ibm1:en-de")
        config.set("Ibm1:en-de", "model", os.path.abspath("../../../res/ibm1/lex.en-de"))       
        
        source_language = "en"
        target_language = "de"

        manager = FeatureGeneratorManager()        
        gateway = LocalJavaGateway()
        
        initialized = manager.initialize_given_feature_generators(generators, config, source_language, target_language, gateway)
        print initialized
        self.assertEqual(len(initialized), 1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_feature_generators']
    unittest.main()