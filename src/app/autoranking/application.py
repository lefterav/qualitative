# -*- coding: utf-8 -*-

'''
Created on 2 Aug 2013

@author: Eleftherios Avramidis
'''

import time
import cPickle as pickle
import sys

from sentence.sentence import SimpleSentence

from ml.lib.orange import OrangeRuntimeRanker 
from sentence.parallelsentence import ParallelSentence

from bootstrap import ExperimentConfigParser
from featuregenerator.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
from featuregenerator.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.bleu.bleugenerator import CrossBleuGenerator, BleuGenerator
from featuregenerator.meteor.meteor import CrossMeteorGenerator, MeteorGenerator
from featuregenerator.attribute_rank import AttributeRankGenerator
from featuregenerator.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.parser.berkeley.berkeleyclient import BerkeleySocketFeatureGenerator
from featuregenerator.preprocessor import Normalizer
from featuregenerator.preprocessor import Tokenizer
from featuregenerator.preprocessor import Truecaser

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient
from py4j.java_gateway import java_import

from util.jvm import JVM


class Autoranking:

    def __init__(self, configfilenames, classifiername):
        cfg = ExperimentConfigParser()
        for config_filename in configfilenames:
            cfg.read(config_filename)

        gateway = self._get_java_gateway(cfg)        
        self.featuregenerators = self.initialize_featuregenerators(cfg, gateway)
        ##self.attset = attset
        
        self.ranker = OrangeRuntimeRanker(classifiername)
        self.source_language =  cfg.get("general", "source_language")
        self.target_language =  cfg.get("general", "target_language")
        
        
    def rank(self, source, translations):
        sourcesentence = SimpleSentence(source)

        translationsentences = [SimpleSentence(t, {"system":"{}".format(i+1)}) for i,t in enumerate(translations)]
        atts = {"langsrc":self.source_language, "langtgt":self.target_language}
        parallelsentence = ParallelSentence(sourcesentence, translationsentences, None, atts)
        
        #annotate the parallelsentence
        annotated_parallelsentence = self._annotate(parallelsentence)
        print "line annotated"
        ranking, description = self.ranker.rank_sentence(annotated_parallelsentence)
        
        #put things in the original order given by the user
        #because the ranker scrambles the order
        ranking.sort(key=lambda x: int(x.get_attribute("system")))
        
        #return only ranks without system ids
        ranking = [r[0] for r in ranking]
        
        return ranking, description
        
        
    def _annotate(self, parallelsentence):
        
        #before parallelizing take care of diverse dependencies on preprocessing
        for featuregenerator in self.featuregenerators:
            sys.stderr.write("Running {} \n".format(str(featuregenerator)))
            parallelsentence = featuregenerator.add_features_parallelsentence(parallelsentence)
            time.sleep(1)
            print "got sentence"
        return parallelsentence
        
        
    def _get_parser(self, cfg, gateway, language):
        for parser_name in [section for section in cfg.sections() if section.startswith("parser:")]:
            if cfg.get(parser_name, "language") == language:
                grammarfile = cfg.get(parser_name, "grammarfile")
                sys.stderr.write("initializing socket parser with grammar file {}\n".format(grammarfile))
                return BerkeleySocketFeatureGenerator(language, grammarfile, gateway)
                
    def _get_java_gateway(self, cfg):
        java_classpath, dir_path = cfg.get_classpath()
        
        if java_classpath:
            
            self.jvm = JVM(java_classpath)
            socket_no = self.jvm.socket_no
            self.gatewayclient = GatewayClient('localhost', socket_no)
            self.gateway = JavaGateway(self.gatewayclient, auto_convert=True, auto_field=True)
            sys.stderr.write("Initialized global Java gateway with pid {} in socket {}\n".format(self.jvm.pid, socket_no))
            return self.gateway


    def initialize_featuregenerators(self, cfg, gateway):
        
        

        source_language =  cfg.get("general", "source_language")
        target_language =  cfg.get("general", "target_language")
        
        src_parser = self._get_parser(cfg, gateway, source_language)
        tgt_parser = self._get_parser(cfg, gateway, target_language)

        langpair = (source_language, target_language)

    
        
        featuregenerators = [
            Normalizer(source_language),
            Normalizer(target_language),
            Tokenizer(source_language),
            Tokenizer(target_language),
            
            #cfg.get_parser(source_language),
            src_parser,
            tgt_parser,
            
            ParserMatches(langpair),
            
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
                       '/home/Eleftherios Avramidis/workspace/qualitative/src/app/autoranking/config/pipeline.cfg',
                       '/home/Eleftherios Avramidis/workspace/qualitative/src/app/autoranking/config/pipeline.wmt13metric.blade6.de.de-en.cfg'
                       ]
            
    
    source = "Wir muessen diese Loesung diskutieren"
    target1 = "We have to discuss this solution"
    target2 = "We have to discuss this"
    target3 = "We must this solution discuss"

    autoranker = Autoranking(configfilenames, classifier_filename)
    result, description = autoranker.rank(source, [target1, target2, target3])
    print result
    print description


