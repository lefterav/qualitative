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
from util.jvm import JVM
from py4j.java_gateway import GatewayClient, JavaGateway


def evaluate_selection(parallelsentences, 
                        metrics=[], 
                        function=max,
                        rank_name="rank_hard",
                        default_system=None,
                        out_filename=None,
                        ref_filename=None,
                        language=None):
    
    selected_sentences = []
    original_sentences = defaultdict(list)
    results = OrderedDict()
    selected_systems = defaultdict(int) #collect the winnings of each system
    
    gateway = JavaGateway(GatewayClient('localhost', JVM(None).socket_no), auto_convert=True, auto_field=True)
 
    
    
    #iterate over all parallelsentences, get the selected ones in a list along with references
    for j, parallelsentence in enumerate(parallelsentences):

        ranking = [int(tgt.get_attribute(rank_name)) for tgt in parallelsentence.get_translations()]
        #get the best sentence according to ranking
        best_rank = function(ranking)

        reference = parallelsentence.get_reference()
        if not reference:
            log.warning("Sentence {} did not have a reference".format(parallelsentence.get_attribute("judgement_id")))
            continue
        #for statistic reasons we collect statistics for all sentences that have the best rank
        counter = 0
        for translation in parallelsentence.get_translations():

            system_name = translation.get_attribute("system")
            original_sentences[system_name].append((translation.get_string(), [reference.get_string()]))
            if int(translation.get_attribute(rank_name)) == int(best_rank):
                selected_systems[system_name] += 1
                #if there is a tie, collect the first sentence that appears TODO:improve
                if counter == 0:
                    selected_sentences.append((translation.get_string(), [reference.get_string()]))
                    counter+=1
                
    
    if j==0:
        raise ValueError("File reader contains no sentences")
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
        if language and gateway:
            metrics.append(MeteorGenerator(language, gateway))
    
    for metric in metrics:
        metric_results = metric.analytic_score_sentences(selected_sentences)
        results.update(metric_results)
        
        for system_name, original_system_sentences in original_sentences.iteritems():
            metric_results = metric.analutic_score_sentences(original_system_sentences)
            metric_results = OrderedDict([("{}_{}".format(system_name, metric_name), values) for metric_name, values in metric_results.iteritems()])
            results.update(metric_results)
        
    with open(out_filename, 'w') as f:
        f.write(os.linesep.join([t for t,_ in selected_sentences]))

    if ref_filename:
        with open(ref_filename, 'w') as f:
            f.write(os.linesep.join([r[0] for _,r in selected_sentences]))

    return results





                         
