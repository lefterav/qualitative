'''
Created on 30 Aug 2012

@author: Eleftherios Avramidis
'''

from dataprocessor.input.jcmlreader import JcmlReader
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml

from featuregenerator.bleu import bleu
from featuregenerator.bleu.bleugenerator import BleuGenerator
from featuregenerator.meteor.meteor import MeteorGenerator
from featuregenerator.levenshtein.levenshtein import levenshtein
import sys
from sentence.parallelsentence import ParallelSentence
from sentence.scoring import Scoring

if __name__ == '__main__':
    datafile = sys.argv[1]
    java_classpath = ["/home/Eleftherios Avramidis/taraxu_tools/meteor-1.3/meteor-1.3.jar","/home/Eleftherios Avramidis/taraxu_tools/meteor-1.3","/usr/share/py4j/py4j0.7.jar","/home/Eleftherios Avramidis/workspace/TaraXUscripts/src/app/autoranking"]
    dir_path = "/home/Eleftherios Avramidis/workspace/TaraXUscripts/src/app/autoranking"
    
    dataset = JcmlReader(datafile).get_dataset()
    meteor = MeteorGenerator("en", java_classpath, dir_path)
    
    for parallelsentence in dataset.parallelsentences:
        reference = parallelsentence.get_reference()
        for translation in parallelsentence.get_translations():
            neg_bleuscore = -bleu.smoothed_score_sentence(translation.get_string(), [reference.get_string()])
            translation.add_attribute("bleu_ref_neg", str(neg_bleuscore))
            
            neg_meteor = -float(meteor.score(translation.get_string(), [reference.get_string()])['meteor_score'])
            translation.add_attribute("meteor_ref_neg", str(neg_meteor))
            
            lev = levenshtein(translation.get_string(), reference.get_string())
            translation.add_attribute("lev", str(lev))
    
    Parallelsentence2Jcml(dataset.parallelsentences).write_to_file( "toscore.jcml")
    
    scoringset = Scoring(dataset)

#    print scoringset.avg_first_ranked("bleu_ref_neg", "rank")
#    print scoringset.avg_predicted_ranked("bleu_ref_neg", "rank")
    for feature in ["bleu_ref_neg", "meteor_ref_neg", "lev"] :
        r = scoringset.get_kendall_tau(feature, "rank")
        s = scoringset.best_predicted_vs_human(feature, "rank")
        
        l = list(s.values())
        print feature, r["tau"], r["avg_seg_tau"], "\t".join([str(i) for i in l])
   