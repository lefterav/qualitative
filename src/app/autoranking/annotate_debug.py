'''
Created on 17 Sep 2012

@author: elav01
'''

import shutil
import os
import re
import sys

#pipeline essentials
from ruffus import *
#from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph, pipeline_printout

#internal code classes
from bootstrap import cfg
from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml 
from io_utils.sax import saxjcml
from featuregenerator.parser.berkeley.parsermatches import ParserMatches
from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
from featuregenerator.ratio_generator import RatioGenerator
from featuregenerator.ibm1featuregenerator import Ibm1FeatureGenerator
from featuregenerator.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.bleu.bleugenerator import CrossBleuGenerator, BleuGenerator
from featuregenerator.meteor.meteor import CrossMeteorGenerator, MeteorGenerator
from featuregenerator.attribute_rank import AttributeRankGenerator
from io_utils.input.xmlreader import XmlReader
from featuregenerator.languagechecker.languagetool_socket import LanguageToolSocketFeatureGenerator
from featuregenerator.preprocessor import Normalizer
from featuregenerator.preprocessor import Tokenizer


def features_checker_target(input_file, output_file, target_language):
#    features_checker(input_file, output_file, language_checker_target)
    cfg.get_checker(target_language).add_features_batch_xml(input_file, output_file)
#    saxjcml.run_features_generator(input_file, output_file, [cfg.get_checker(target_language)])
    
if __name__ == '__main__':
    #"/home/elav01/Desktop/wmt2008-de-en-jcml-rank.orig.debug2.jcml", "/home/elav01/Desktop/wmt2008-de-en-jcml-rank.orig.debug2.annotated.jcml", "en")
    print features_checker_target("/local/elav01/selection-mechanism/autoranking/21/wmt2008-de-en-jcml-rank.orig.jcml", "/local/elav01/selection-mechanism/autoranking/21/wmt2008-de-en-jcml-rank.iq.en.f.jcml", "en") 
