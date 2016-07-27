'''
Created on 19 Apr 2016
@author: Eleftherios Avramidis
'''
import pickle

from app.autoranking.application import Autoranking
from app.autoranking.bootstrap import ExperimentConfigParser
from featuregenerator.blackbox.counts import LengthFeatureGenerator
from featuregenerator.blackbox.ibm1 import AlignmentFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgAlignmentFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.preprocessor import Normalizer, Tokenizer, Truecaser
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator

class SystemSelector(Autoranking):
    def __init__(self, configfilenames, classifiername, reverse=False):
        """Autoranking
        Initialize the class.
        @param configfilenames: a list of annotation configuration files that contain
        the settings for all feature generators etc.
        @type configfilenames: list(str)
        @param classifiername: the filename of a picked learner object
        @type classifiername: str
        """
        cfg = ExperimentConfigParser()
        for config_filename in configfilenames:
            cfg.read(config_filename)
        
        self.gateway = cfg.java_init()
        self.reverse = reverse
        
        self.featuregenerators = self.initialize_featuregenerators(cfg)
        self.ranker = pickle.load(open(classifiername))
        self.source_language = cfg.get("general", "source_language")
        self.target_language = cfg.get("general", "target_language")
    
    def initialize_featuregenerators(self, cfg):
        """
        Initialize the featuregenerators that handle superficial analysis of given translations
        @param cfg: the loaded configuration object
        """
        source_language =  cfg.get("general", "source_language")
        target_language =  cfg.get("general", "target_language")
        
        src_parser = cfg.get_parser(source_language)
        tgt_parser = cfg.get_parser(target_language)

        langpair = (source_language, target_language)
        
        #attset_242_source = "lm_unk,l_tokens,berkeley-n,parse-VP,berkley-loglikelihood"
        #attset_242_target = "lm_prob,lm_unk,l_tokens,berkeley-n,parse-VP,berkley-loglikelihood,cfgal_unaligned,ibm1-score,ibm1-score-inv,l_avgoccurences,cfg_fulldepth,parse-comma,parse-dot,parse_S_depth_max,parse_S_depth_min,cfgpos_S-VP,cfgpos_end_VP-VZ,cfgpos_end_VP-VP,cfgpos_VP-VP,cfgpos_end_VP-VVINF,cfgpos_VP-VVINF,cfgpos_VP-VB,cfgpos_VP-VBZ,cfgpos_end_S-VVPP,cfgpos_VP-VBG,lt_UNPAIRED_BRACKETS,lt_DE_COMPOUNDS"

        featuregenerators = [
            Normalizer(source_language),
            Normalizer(target_language),
            Tokenizer(source_language),
            Tokenizer(target_language),
            
            src_parser,
            tgt_parser,
            
            ParserMatches(langpair),
            
            #truecase only for the language model
            Truecaser(source_language, cfg.get_truecaser_model(source_language)),
            Truecaser(target_language, cfg.get_truecaser_model(target_language)),
            
            cfg.get_lm(source_language),
            cfg.get_lm(target_language),    
                    
            AlignmentFeatureGenerator(cfg.get("ibm1:{}-{}".format(source_language, target_language), "lexicon"), 
                                      cfg.get("ibm1:{}-{}".format(target_language, source_language), "lexicon")),
            CfgAlignmentFeatureGenerator(),
            #LanguageToolSocketFeatureGenerator(target_language, self.gateway),
            CrossMeteorGenerator(target_language, self.gateway),
            LengthFeatureGenerator()
        ]
        
        return featuregenerators