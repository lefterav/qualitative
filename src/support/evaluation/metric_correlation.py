'''
Created on 30 Aug 2012

@author: lefterav
'''

from io_utils.input.jcmlreader import JcmlReader
from featuregenerator.bleu import bleu
from featuregenerator.bleu.bleugenerator import BleuGenerator
from featuregenerator.meteor.meteor import MeteorGenerator
import sys
from sentence.parallelsentence import ParallelSentence
from sentence.scoring import Scoring

if __name__ == '__main__':
    datafile = sys.argv[1]
    java_classpath = ["/home/elav01/taraxu_tools/meteor-1.3/meteor-1.3.jar","/home/elav01/taraxu_tools/meteor-1.3","/usr/share/py4j/py4j0.7.jar","/home/elav01/workspace/TaraXUscripts/src/experiment/autoranking"]
    dir_path = "/home/elav01/workspace/TaraXUscripts/src/experiment/autoranking"
    
    dataset = JcmlReader(datafile).get_dataset()
    meteor = MeteorGenerator("en", java_classpath, dir_path)
    
    for parallelsentence in dataset.parallelsentences:
        reference = parallelsentence.get_reference()
        for translation in parallelsentence.get_translations():
            neg_bleuscore = -bleu.smoothed_score_sentence(translation.get_string(), [reference.get_string()])
            translation.add_attribute("bleu_ref_neg", neg_bleuscore)
            
            neg_meteor = -float(meteor.score(translation.get_string(), [reference.get_string()])['meteor_score'])
            translation.add_attribute("meteor_ref_neg", str(neg_meteor))
    
    scoringset = Scoring(dataset)
    print scoringset.get_kendall_tau("bleu_ref_neg", "rank")
    print scoringset.get_kendall_tau("meteor_ref_neg", "rank")