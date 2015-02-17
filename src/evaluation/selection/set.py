'''
Created on 16 Feb 2015

@author: Eleftherios Avramidis
'''
from collections import defaultdict, OrderedDict
from featuregenerator.reference.bleu import BleuGenerator
from featuregenerator.reference.meteor.meteor import MeteorGenerator 
import os
from featuregenerator.reference.levenshtein.levenshtein_generator import LevenshteinGenerator
from featuregenerator.reference.rgbf import RgbfGenerator
from featuregenerator.reference.wer.werfeaturegenerator import WERFeatureGenerator
from featuregenerator.reference.hjerson import Hjerson
import logging as log

def evaluate_selection(parallelsentences, 
                        metrics=[], 
                        function=max,
                        rank_name="rank_hard",
                        default_system=None,
                        out_filename=None,
                        ref_filename=None):
    
    selected_sentences = []
    results = OrderedDict()
    selected_systems = defaultdict(int) #collect the winnings of each system
    
    
    #iterate over all parallelsentences, get the selected ones in a list along with references
    for parallelsentence in parallelsentences:

        ranking = [tgt.get_attribute(rank_name) for tgt in parallelsentence.get_translations()]
        log.debug("ranking: {}".format(ranking))
        #get the best sentence according to ranking
        best_rank = function(ranking)
        log.debug("Best rank: {}".format(best_rank))

        reference = parallelsentence.get_reference()
        #for statistic reasons we collect statistics for all sentences that have the best rank
        for counter, translation in enumerate(parallelsentence.get_translations()):
            log.debug("Sentence rank: {} {}".format(translation.get_attribute("system"), translation.get_attribute(rank_name)))

            if int(translation.get_attribute(rank_name)) == int(best_rank):
                system_name = translation.get_attribute("system")
                selected_systems[system_name] += 1
                if counter == 0:
                    selected_sentences.append((translation.get_string(), [reference.get_string()]))
    
    for system_name, counts in selected_systems.iteritems():
        results["sel-counts_{}".format(system_name)] = counts
        results["sel-perc_{}".format(system_name)] = 1.00*counts/len(selected_sentences)

    #generate a default list of metric objects, if not specified by parameters
    if not metrics:
        metrics = [LevenshteinGenerator(),
                 BleuGenerator(),
                 RgbfGenerator(),
                 WERFeatureGenerator(),
                 Hjerson()]
    
    for metric in metrics:
        results.update(metric.analytic_score_sentences(selected_sentences))
        
    with open(out_filename, 'w') as f:
        f.write(os.linesep.join([t for t,_ in selected_sentences]))
    
    with open(ref_filename, 'w') as f:
        f.write(os.linesep.join([r for _,r in selected_sentences]))

    return results





                         
