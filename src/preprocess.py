#!/usr/bin/python

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
    exp = Experiment()
    
    if sys.argv[1] == "readwmt":
        dir = "/home/lefterav/taraxu_data/wmt11-data"
        langpair = "de-en"
        outfile = "/home/lefterav/taraxu_data/wmt11-data/wmt11.jcml"
        exp.convert_wmtdata(dir, langpair, outfile)
        
    elif sys.argv[1] == "wmt11eval":
        sourcefile = sys.argv[2]
        
        #print "language model features"
        #lmfile = sourcefile.replace("jcml", "lm.1.jcml")
        #exp.add_ngram_features_batch(sourcefile, lmfile)
        
        #print "parser features"
        #bpfile = sourcefile.replace("jcml", "bp.2.jcml")
        #exp.add_b_features_batch(lmfile, bpfile, "http://localhost:8682", "en")
        
        #print "german parser features"
        bpfile1 = sourcefile.replace("jcml", "bp.2b.jcml")
        #exp.add_b_features_batch(bpfile, bpfile1, "http://localhost:8683", "de")
        
        print "final features"
        exfile = sourcefile.replace("jcml", "ex.3.jcml")
        exp.analyze_external_features(bpfile1, exfile) 
        
    elif sys.argv[1] == "jcml2wmt":
        sourcefile = sys.argv[2]
        filename_out = sourcefile.replace("jcml", "%d.tab")
        reader = XmlReader(sourcefile)
        from io.output.wmt11tabwriter import Wmt11TabWriter
        
        i = 0
        filenames = []
        n = reader.length()
        while i < n:
            k = i + 100
            if k >= n:
                k = n - 1
            classified_xmlwriter = Wmt11TabWriter(None, "dfki_parseconf")
            classified_xmlwriter.write_to_file_nobuffer(filename_out % i, reader.get_parallelsentences(i, k))
            filenames.append(filename_out % i) 
            i = k + 1
        import commands
        commands.getstatusoutput("cat %s > %s", (" ".join(filenames), sourcefile.replace("jcml", "tab") ) )
        commands.getstatusoutput("rm %s", " ".join(filenames) )
