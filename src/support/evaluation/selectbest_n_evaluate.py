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


def sort_sentences_per_system(dataset, predicted_rank_name, original_rank_name):
    sentences_per_system={}
    for parallelsentence in dataset:
        
        reference = parallelsentence.get_reference()
        reference_string = reference.get_string()
        
        predicted_rank_vector = [float(f) for f in parallelsentence.get_filtered_target_attribute_values(predicted_rank_name, "system", "_ref")]
        original_rank_vector = [float(f) for f in parallelsentence.get_filtered_target_attribute_values(original_rank_name, "system", "_ref")]
        
        min_predicted = min(predicted_rank_vector)     
        min_original = min(original_rank_vector)
        max_original = max(original_rank_vector)
        
            
        predicted_best = False
        
        parallelsentence_strings = {} 
        
        for translation in parallelsentence.get_translations():
            
            
            translation_string = translation.get_string()
            
            #first gather based on the system name
            system = translation.get_attribute("system")
            sentence_tuple = ([translation_string], [reference_string])    
            sentences_per_system.setdefault(system, []).append(sentence_tuple)

            system_categories = [
                                 ('-predicted_best', predicted_rank_name, min_predicted),
                                 ("-human_1", original_rank_name, min_original),
                                 ("-human_2", original_rank_name, min_original+1),
                                 ("-human_3", original_rank_name, min_original+2),
                                 ("-human_4", original_rank_name, min_original+3),
                                 ("-human_worst", original_rank_name, max_original)
                                ]
        
            
        
            for id, attname, attvalue in system_categories:
                if float(translation.get_attribute(attname)) == attvalue:
                    parallelsentence_strings.setdefault(id, []).append(translation_string)
        
        for id, translation_strings in parallelsentence_strings.iteritems():
            sentence_tuple = (translation_strings, reference_string)
            sentences_per_system.setdefault(id, []).append(sentence_tuple)
            
                
    return sentences_per_system

if __name__ == '__main__':
    datafile = sys.argv[1]
    
        
    java_classpath = ["/home/elav01/taraxu_tools/meteor-1.3/meteor-1.3.jar","/home/elav01/taraxu_tools/meteor-1.3","/usr/share/py4j/py4j0.7.jar","/home/elav01/workspace/TaraXUscripts/src/experiment/autoranking"]
    dir_path = "/home/elav01/workspace/TaraXUscripts/src/experiment/autoranking"
    #meteor = MeteorGenerator("en", java_classpath, dir_path)
    
    scorers = [bleu] 
    #, meteor]
    
    dataset = JcmlReader(datafile).get_dataset()
    
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
    
    sentences_per_system = sort_sentences_per_system(dataset, predicted_rank_name, original_rank_name)        
    
    for scorer in scorers:
        print
        print "----------------"        
        print scorer.__name__
        print "----------------"
        for system, sentence_tuples in sorted(sentences_per_system.items()):
            print system, "&", round(100.00*scorer.score_multitarget_sentences(sentence_tuples),2), "&", len(sentence_tuples), " \\\\"
        
        