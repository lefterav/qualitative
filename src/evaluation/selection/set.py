'''
Created on 16 Feb 2015

@author: Eleftherios Avramidis
'''
from collections import defaultdict, OrderedDict
from operator import attrgetter
from featuregenerator.reference.bleu import BleuMetric


def evaluate_selections(parallelsentences, 
                        metrics=[], 
                        function=max,
                        rank_name="rank-predicted",
                        default_system=None
                        out_filename=None):
    selected_sentences = []
    results = OrderedDict()
    selected_systems = defaultdict(int) #collect the winnings of each system
    
    #iterate over all parallelsentences, get the selected ones in a list along with references
    for parallelsentence in parallelsentences:
        ranking = parallelsentence.get_ranking()
        #get the best sentence according to ranking
        best_rank = function(ranking)
        reference = parallelsentence.get_reference()
        #for statistic reasons we collect statistics for all sentences that have the best rank
        for counter, translation in enumerate(parallelsentence.get_translations()):
            if translation.get_attribute(rank_name) == best_rank:
                system_name = translation.get_attribute("system")
                selected_systems[system_name] += 1
                if (default_system and default_system == system_name) or (not default_system and counter == 0):
                    selected_sentences.append((translation.get_string(), [reference.get_string()]))
    
    for system_name, counts in selected_systems.iteritems():
        results["sel-counts_{}".format(system_name)] = counts
        results["sel-perc_{}".format(system_name)] = 1.00*counts/len(selected_sentences)

    for metric in metrics:
        results.update(metric.full_score_sentences(selected_sentences))

    return results





                         
