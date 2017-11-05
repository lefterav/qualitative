'''
Process a test set with ranks already assigned, and count the amount of ties per MT-system pair 

Created on Nov 4, 2017

@author: lefterav
'''

from dataprocessor.ce.cejcml import CEJcmlReader
from sentence.ranking import Ranking
import itertools
from collections import defaultdict, OrderedDict
import sys
from operator import itemgetter
from evaluation.selection.set import evaluate_selection
from featuregenerator.reference.bleu import BleuGenerator
 

def process_file(filenames, rank_name="rank_hard"):
    ties_counter = defaultdict(int)
    metric_scores = OrderedDict()
    for filename in filenames:
        reader = CEJcmlReader(filename, desired_target=['system','rank_hard', 'rank_soft'])
        metric_scores.update(evaluate_selection(reader, [BleuGenerator()]))                      
  
        #print metric_scores
        reader = CEJcmlReader(filename, desired_target=['system','rank_hard', 'rank_soft'])
        
        for parallelsentence in reader:
            ranks = Ranking(parallelsentence.get_filtered_target_attribute_values(rank_name, 
                                                                                            filter_attribute_name="system", 
                                                                                            filter_attribute_value="_ref",
                                                                                            sub=-1))
            systems = parallelsentence.get_target_attribute_values('system')
            ranks = ranks.normalize(ties='ceiling')
            system_rank_tuples = zip(systems, ranks)
            
            for (system1, rank1), (system2, rank2) in itertools.combinations(system_rank_tuples, 2):
                if rank1 == rank2 and rank1!=-1 and rank2!=-1:
                    ties_counter[(system1, system2)]+=1

    
    ties_counter_tuples = ties_counter.items()
    ties_counter_tuples = sorted(ties_counter_tuples, key=itemgetter(1), reverse=True)
    errors = 0
    for (system1, system2), ties_counts in ties_counter_tuples:
        try:
            bleu1 = metric_scores["{}_bleu-4gram".format(system1)]
            bleu2 = metric_scores["{}_bleu-4gram".format(system2)]
            bleudiff = round(abs(bleu1-bleu2),3) 
            print system1, system2, ties_counts, bleudiff
        except KeyError:
            errors+=1
            pass
    print "errors: ", errors 
    
if __name__ == '__main__':
    filenames = sys.argv[1:]
    print "Processing filenames", filenames
    process_file(filenames)