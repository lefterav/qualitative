'''
Created on 30 Aug 2012

@author: lefterav
'''

from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.output.xmlwriter import XmlWriter

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
    #meteor = MeteorGenerator("en", java_classpath, dir_path)
    
    #optional 
    if len(sys.argv) == 3:
        importfile = str(sys.argv[2])
#        sys.stderr("Importing references from file {}".format(importfile))
        importdataset = JcmlReader(importfile).get_dataset()
        dataset.merge_dataset(importdataset, add_missing=False)  
#        XmlWriter(dataset).write_to_file(datafile.replace("jcml", "merged.jcml"))
    predicted_first_sentences = []
    original_first_sentences = []
    original_last_sentences = []
    
    predicted_rank_name = "rank_soft"
    original_rank_name = "rank"
    
    sentences_per_system={}
    for parallelsentence in dataset:
        
        reference = parallelsentence.get_reference()
        
        predicted_rank_vector = parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")
        original_rank_vector = parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")
        
        min_predicted = min(predicted_rank_vector)     
        min_original = min(original_rank_vector)
        max_original = max(original_rank_vector)
        
        
        for translation in parallelsentence.get_translations():
            if translation.get_attribute(predicted_rank_name) == min_predicted:
                predicted_first_sentences.append((translation.get_string(), [reference.get_string()]))
                break
        for translation in parallelsentence.get_translations():
            if translation.get_attribute(original_rank_name) == min_original:
                original_first_sentences.append((translation.get_string(), [reference.get_string()]))
                break
        for translation in parallelsentence.get_translations():
            if translation.get_attribute(original_rank_name) == max_original:
                original_last_sentences.append((translation.get_string(), [reference.get_string()]))
                break
            
        for translation in parallelsentence.get_translations():
            system = translation.get_attribute("system")
            translation_string = translation.get_string()
            reference_string = reference.get_string()
            sentence_tuple = (translation_string, [reference_string])    
            sentences_per_system.setdefault(system, []).append(sentence_tuple)
        
    
    for system, sentence_tuples in sentences_per_system.iteritems():
        print system, round(100.00*bleu.score_sentences(sentence_tuples),2), len(sentence_tuples)
        
    
    print
        
            
    bleuscore_gold = round(100.00*bleu.score_sentences(original_first_sentences),2)
    bleuscore_worst = round(100.00*bleu.score_sentences(original_last_sentences),2)
    bleuscore_predicted = round(100.00*bleu.score_sentences(predicted_first_sentences),2)
    
    print "Best", bleuscore_gold
    print "worst", bleuscore_worst
    print "ours", bleuscore_predicted
    print
    