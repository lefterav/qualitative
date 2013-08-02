# -*- coding: utf-8 -*-

'''
Created on 2 Aug 2013

@author: Eleftherios Avramidis
'''

import cPickle as pickle
from sentence.sentence import SimpleSentence

from ml.lib.orange import OrangeRuntimeRanker 
from sentence.parallelsentence import ParallelSentence


from experiment.autoranking.bootstrap import ExperimentConfigParser
from featuregenerator.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
from featuregenerator.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.bleu.bleugenerator import CrossBleuGenerator, BleuGenerator
from featuregenerator.meteor.meteor import CrossMeteorGenerator, MeteorGenerator
from featuregenerator.attribute_rank import AttributeRankGenerator
from featuregenerator.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.preprocessor import Normalizer
from featuregenerator.preprocessor import Tokenizer
from featuregenerator.preprocessor import Truecaser



class Autoranking:

    def __init__(self, configfilenames, classifiername):
        cfg = ExperimentConfigParser()
        for config_filename in configfilenames:
            cfg.read(config_filename)

        self.featuregenerators = self.initialize_featuregenerators(cfg)
#         self.attset = attset
        self.ranker = OrangeRuntimeRanker(classifiername)
        
        
    def rank(self, source, translations):
        sourcesentence = SimpleSentence(source)
        translationsentences = [SimpleSentence(t) for t in translations]
        parallelsentence = ParallelSentence(sourcesentence, translationsentences)
        
        #annotate the parallelsentence
        annotated_parallelsentence = self._annotate(parallelsentence)
        ranking = self.ranker.rank_sentence(annotated_parallelsentence)
        
        return ranking
        
    def _annotate(self, parallelsentence):
        
        #before parallelizing take care of diverse dependencies on preprocessing
        for featuregenerator in self.featuregenerators:
            parallelsentence = featuregenerator.add_features_parallelsentence(parallelsentence)
        return parallelsentence


    def initialize_featuregenerators(self, cfg):
        
        gateway = cfg.java_init()
        source_language =  cfg.get("general", "source_language")
        target_language =  cfg.get("general", "target_language")
        
        
        featuregenerators = [
            Normalizer(source_language),
            Normalizer(target_language),
            Tokenizer(source_language),
            Tokenizer(target_language),
            
            cfg.get_parser(source_language),
            cfg.get_parser(target_language),
            
            #truecase
            Truecaser(source_language, cfg.get_truecaser_model(source_language)),
            Truecaser(target_language, cfg.get_truecaser_model(target_language)),
            
            cfg.get_lm(source_language),
            cfg.get_lm(target_language),            

            CrossMeteorGenerator(target_language, cfg.get_classpath()[0], cfg.get_classpath()[1]),
            
            LengthFeatureGenerator()
        ]
        
        return featuregenerators
        

if __name__ == "__main__":
    
    classifier_filename = "/share/taraxu/selection-mechanism/wmt13/sentenceranking/autoranking_wmt13_newfeatures1_de_en/class_nameranklangpairde-eninclude_references0.0ties0.0trainset_modeannotatedattattset_24classifierLogReg/classifier.clsf"
    configfilenames = [
                       '/home/elav01/workspace/qualitative/src/experiment/autoranking/config/pipeline.cfg',
                       '/home/elav01/workspace/qualitative/src/experiment/autoranking/config/pipeline.blades.cfg'
                       ]
            
    
    source = "Wir müssen diese Lösung diskutieren"
    target1 = "We have to discuss this solution"
    target2 = "This solution have we to discuss"
    target3 = "We must this solution discuss"

    autoranker = Autoranking(configfilenames, classifier_filename)
    print autoranker.rank(source, [target1, target2, target3])