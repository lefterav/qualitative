'''
Created on 19 Apr 2016
@author: Eleftherios Avramidis
'''
import pickle

from featuregenerator.blackbox.counts import LengthFeatureGenerator
from featuregenerator.blackbox.ibm1 import Ibm1FeatureGenerator
from featuregenerator.blackbox.parser.berkeley.cfgrules import CfgAlignmentFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.preprocessor import Normalizer, Tokenizer, Truecaser,\
    Detruecaser, Detokenizer
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator
from ConfigParser import SafeConfigParser

import time
import sys
import logging as log

from featuregenerator.blackbox.parser.berkeley.berkeleyclient import BerkeleyLocalFeatureGenerator
from sentence.sentence import SimpleSentence

from ml.lib.orange.ranking import OrangeRanker 
from sentence.parallelsentence import ParallelSentence
from featuregenerator.sentencesplitter import SentenceSplitter

from featuregenerator.blackbox.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.blackbox.counts import LengthFeatureGenerator
from featuregenerator.reference.meteor.meteor import CrossMeteorGenerator
from featuregenerator.preprocessor import Normalizer
from featuregenerator.preprocessor import Tokenizer
from featuregenerator.preprocessor import Truecaser

from py4j.java_gateway import GatewayClient, JavaGateway 
import pickle
from featuregenerator import FeatureGeneratorManager
from ConfigParser import SafeConfigParser
from util.jvm import LocalJavaGateway
from collections import OrderedDict


class Autoranking:
    """
    A class that demonstrates the use of simple ranking pipeline. It provides
    the function 'parse' that receives source and translation strings and
    returns a ranked list
    @ivar featuregenerators: List of initialized feature generator objects in the order that will be used 
    @type featuregenerators: [featuregenerator.featuregenerator.FeatureGenerator, ...]
    @ivar ranker: Machine Learning class that handles ranking of items
    @type ranker: ml.lib.orange
    @ivar source_language: Language code for source language
    @type source_language: str
    @ivar target_language: Language code for target language
    @type target_language: str
    """
    def __init__(self, config_files, model, source_language=None, 
                 target_language=None, reverse=False):
        """
        Initialize the class.
        @param config_files: a list of annotation configuration files that contain
        the settings for all feature generators etc.
        @type config_files: list(str)
        @param model: the model of the model of a picked learner object
        @type model: str
        @param source_language: Language code for source language
        @type source_language: str
        @param target_language: Language code for target language
        @type target_language: str
        """
        #TODO: shouldn't the language pair also be stored along with the model?

        #retrieve the ranking model from the given file
        try:
            self.ranker = pickle.load(model)
        except:
            self.ranker = pickle.load(open(model))
        
        #read configuration for language resources
        config = SafeConfigParser({'java': 'java'})
        config.read(config_files)
        
        #initialize a java gateway 
        #TODO: find a way to avoid loading java if not required by generators
        gateway = LocalJavaGateway(config.get("general", "java"))
        
        #whether the ranks should be reversed before used
        self.reverse = reverse
        
        #get the required attributes
        self.featureset = self.ranker.attribute_set
        featuregenerator_manager = FeatureGeneratorManager()
        self.pipeline = featuregenerator_manager.get_parallel_features_pipeline(self.featureset, config, source_language, target_language, gateway)
        
        #self.featuregenerators = self.pipeline
        #log.info("pipeline: {}".format(self.featuregenerators))

        self.source_language = source_language
        self.target_language = target_language

        self.preprocessors = [
            Normalizer(source_language),
            Normalizer(target_language),
            Tokenizer(source_language, config.get("Tokenizer:{}".format(source_language), "protected", None)),
            Tokenizer(target_language, config.get("Tokenizer:{}".format(target_language), "protected", None)),
            Truecaser(source_language, config.get("Truecaser:{}".format(source_language), "model")),
            Truecaser(target_language, config.get("Truecaser:{}".format(target_language), "model")),
        ]
        
        #TODO: change this, so that the original output of the system is used
        # without double detokenization 
        self.postprocessors = [
                               Detruecaser(target_language),
                               Detokenizer(target_language)]

        self.source_sentencesplitter = SentenceSplitter({'language': source_language})
        self.translation_sentencesplitter = SentenceSplitter({'language': target_language})
        
    def rank_strings(self, source, translations, reconstruct='soft'):
        # TODO: obsolete function. remove
        """
        Rank translations according to their estimated quality
        @param source: The source sentence whose translations are ranked
        @type source: C{str}
        @param translations: The translations to be ranked
        @type translations: [C{str}, ...]
        """
        sourcesentence = SimpleSentence(source)
        translationsentences = [SimpleSentence(t, {"system" : "{}".format(i+1)}) for i,t in enumerate(translations)]
        atts = {"langsrc" : self.source_language, "langtgt" : self.target_language}
        parallelsentence = ParallelSentence(sourcesentence, translationsentences, None, atts)
        return self.rank_parallelsentence(parallelsentence)
    
    def get_ranked_sentence(self, parallelsentence, new_rank_name="rank_soft", reconstruct="soft"):
        annotated_parallelsentence = self._annotate(parallelsentence)
        ranked_sentence, description = self.ranker.get_ranked_sentence(annotated_parallelsentence, 
                                                                       new_rank_name=new_rank_name, 
                                                                       reconstruct=reconstruct)
        ranked_sentence = self._postprocess(ranked_sentence)
        # add a dictionary of information about the ranking
        ranking_description = OrderedDict()
        for translation in ranked_sentence.get_translations():
            ranking_description[translation.get_system_name()] = {'rank' : translation.get_attribute(new_rank_name),
                                                                  'string' : translation.get_string()}
            log.debug("Augmenting description for {}".format(translation.get_system_name()))
        description['ranking'] = ranking_description
        log.debug("Description: {}".format(description))
        #TODO: maybe description should not be returned, as it is already contained in the ranked_sentence arguments
        return ranked_sentence, description
    
    def get_best_sentence(self, parallelsentence, new_rank_name="rank_soft", reconstruct="soft", engines=[]):
        if not engines:
            engines = parallelsentence.get_system_names()
        ranked_sentence, description = self.get_ranked_sentence(parallelsentence, new_rank_name, reconstruct)
        best_translation = ranked_sentence.get_best_translation(systems_order=engines, new_rank_name=new_rank_name,
                                                                reverse=self.reverse)
        return best_translation.get_string(), ranked_sentence, description
    
    def _split_sentences(self, text, splitter):
        try:
            strings = splitter.split_sentences(text)
        except UnicodeDecodeError:
            try:
                text = unicode(text, errors='replace')
                strings = self.splitter.split_sentences(text)
            except:
                strings = [""]
        return strings
    
    def get_ranked_sentences_from_strings(self, source_string, translation_strings, system_names=[],
                                          new_rank_name="rank_soft", reconstruct="soft",
                                          request_id=None):
        if not system_names:
            system_names = [str(i) for i in range(1, len(translation_strings)+1)]
        
        # split source text into sentences and create a sentence object for each
        source_sentence_strings = self._split_sentences(source_string, self.source_sentencesplitter)
        source_sentences = [SimpleSentence(s, {}) for s in source_sentence_strings]
        
        # create a dict to associate sentences 
        translations_per_source_sentence = OrderedDict()
        
        # iterate for each system-made translation
        for translation_string, system_name in zip(translation_strings, system_names):
            # split each translation into sentences and map them to the respective sources
            translation_sentence_strings = self._split_sentences(translation_string, self.translation_sentencesplitter)
            for source_sentence, translation_sentence_string in zip(source_sentences, translation_sentence_strings):
                translation = SimpleSentence(translation_sentence_string, {'system': system_name})
                translations_per_source_sentence.setdefault(source_sentence, default=[]).append(translation)
        
        ranked_sentences = []
        # generate parallel sentence objects from the pairs of source and list of translations
        atts = {"langsrc" : self.source_language, "langtgt" : self.target_language}
        
        # add a sentence id as a parallelsentence argument
        if request_id:
            atts['request_id'] = request_id
        
        sentence_id = 0
        for source_sentence, translations in translations_per_source_sentence.iteritems():
            # create a unique id for the sentence
            sentence_id+=1
            if request_id:
                atts['sentence_id'] = "{}_{}".format(request_id, sentence_id)
            else:
                atts['sentence_id'] = sentence_id
            parallelsentence = ParallelSentence(source_sentence, translations, attributes=atts)
            ranked_sentence, _ = self.get_ranked_sentence(parallelsentence, new_rank_name, reconstruct)
            ranked_sentences.append(ranked_sentence)
        return ranked_sentences
            
    
    def get_best_sentence_from_strings(self, source_string, translation_strings, system_names=[],
                                       new_rank_name="rank_soft", reconstruct="soft", request_id=None):
        ranked_sentences = self.get_ranked_sentences_from_strings(source_string, translation_strings, 
                                                                  system_names, new_rank_name, reconstruct,
                                                                  request_id=request_id)
        best_translation_strings = [r.get_best_translation(systems_order=system_names, new_rank_name=new_rank_name,
                                                           reverse=self.reverse).get_string() 
                                    for r in ranked_sentences]
        return " ".join(best_translation_strings), ranked_sentences
    
    def rank_parallelsentence(self, parallelsentence):
        # TODO: obsolete function. remove
        
        #annotate the parallelsentence
        annotated_parallelsentence = self._annotate(parallelsentence)
        log.info("line annotated")
        ranking, description = self.ranker.rank_sentence(annotated_parallelsentence)
        
        #put things in the original order given by the user
        #because the ranker scrambles the order
        ranking.sort(key=lambda x: x[1].get_attribute("system"))
        
        if self.reverse:
            ranking.reverse()
            
        #return only ranks without system ids
        description += "Final ranking: {}".format([(r[0], r[1].get_system_name(), r[1].get_string()) for r in ranking])
        ranking = [r[0] for r in ranking]
        return ranking, description
    
#     def get_ranked_sentence(self, sourcesentence, translationsentences):
#         atts = {"langsrc":self.source_language, "langtgt":self.target_language}
#         parallelsentence = ParallelSentence(sourcesentence, translationsentences, None, atts)
#         annotated_parallelsentence = self._annotate(parallelsentence)
#         ranked_sentence, description = self.ranker.get_ranked_sentence(annotated_parallelsentence)
#         return ranked_sentence, description
        
    def _annotate(self, parallelsentence):
        
        #TODO: parallelize source target
        #TODO: before parallelizing take care of diverse dependencies on preprocessing
        
        for preprocessor in self.preprocessors:
            parallelsentence = preprocessor.add_features_parallelsentence(parallelsentence)
            if not parallelsentence:
                log.info("Bingo: {}".format(preprocessor.__class__.__name__))
        
        parallelsentence = self.pipeline.annotate_parallelsentence(parallelsentence)
        log.debug("Annotated parallel sentence: {}".format(parallelsentence))
        return parallelsentence
    
    def _postprocess(self, parallelsentence):
        for postprocessor in self.postprocessors:
            parallelsentence = postprocessor.add_features_parallelsentence(parallelsentence)
        return parallelsentence
