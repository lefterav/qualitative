'''
@author: lefterav
'''

from io.input.xmlreader import XmlReader
from io.output.xmlwriter import XmlWriter
from os import getenv
import os
from sentence.dataset import DataSet
import codecs
from sentence.rankhandler import RankHandler
import sys
from io.saxjcml import SaxJCMLProcessor
from xml.sax import make_parser


class Experiment:
    def __init__(self):
        pass 
    def add_b_features_batch(self, filename, filename_out, server, language):
        reader = XmlReader(filename)
        parallelsentences = reader.get_parallelsentences()
        reader = None
        from featuregenerator.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator
        parser_en = BerkeleyFeatureGenerator(server, language)
        parallesentences = parser_en.add_features_batch(parallelsentences);
        
        writer = XmlWriter(parallesentences)
        writer.write_to_file(filename_out)

    def analyze_external_features(self, filename, filename_out):
        from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
        from featuregenerator.parser.berkeley.parsermatches import ParserMatches
#        from featuregenerator.lm.srilm.srilmclient import SRILMFeatureGenerator
#        from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
        from featuregenerator.ratio_generator import RatioGenerator
        
        input_file_object = codecs.open(filename, 'r', 'utf-8')
        output_input_file_object = codecs.open(filename_out, 'w', 'utf-8')
                
        #srilm_de = SRILMFeatureGenerator("http://134.96.187.4:8586", "de" )
        #srilm_ngram_de = SRILMngramGenerator("http://134.96.187.4:8585", "de" )
        parsematches = ParserMatches()
        ratio_generator = RatioGenerator()
        lfg = LengthFeatureGenerator()  
        featuregenerators = [lfg, parsematches, ratio_generator]
        #proceed with parcing
        saxreader = SaxJCMLProcessor(output_input_file_object, featuregenerators)
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)


if __name__ == '__main__':
    pass