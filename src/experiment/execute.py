'''
Created on Aug 31, 2011

@author: elav01
'''

from phase import Phase
from task import *
from data import Data
from experiment import Experiment

if __name__ == '__main__':
    
    src_language = "de"
    tgt_language = "en"
    
    tgt_srilmserver = ""
    src_berkeleyserver = ""
    tgt_berkeleyserver = ""
    
    
    experiment = Experiment()
    experiment.input = "/home/elav01/taraxu_data/tmp.exp/wmt09.jcml"
    
    
    #===========================================================================
    # Preprocessing
    #===========================================================================
    preprocessing = Phase()
    preprocessing.name = "generating primary features"
#    tgt_ngram = SerialTask()
#    tgt_ngram.name = "tgt_ngram"
#    from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
#    tgt_ngram.processors = [SRILMngramGenerator(tgt_srilmserver, tgt_language)]
    
#    src_berkeley = SerialTask()
#    src_berkeley.name = "src_berkeley"
#    from featuregenerator.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator        
#    src_berkeley.processors = [BerkeleyFeatureGenerator(src_berkeleyserver, src_language)]
#    
#    tgt_berkeley = SerialTask()
#    tgt_berkeley.name = "tgt_berkeley"
#    tgt_berkeley.processors = [BerkeleyFeatureGenerator(tgt_berkeleyserver, tgt_language)]
#    
    analyzefeatures = SerialTask()
    analyzefeatures.name = "analyze_features"
    analyzefeatures.file_extension = "ef"
    #analyzefeatures.required = [src_berkeley, tgt_berkeley]
    
    from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
    from featuregenerator.parser.berkeley.parsermatches import ParserMatches
    from featuregenerator.ratio_generator import RatioGenerator

    analyzefeatures.processors = [LengthFeatureGenerator()]

   
    preprocessing.tasks = [analyzefeatures]   
    
    experiment.phases = [preprocessing]
    experiment.run()