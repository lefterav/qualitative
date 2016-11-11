'''
Utility script that measures the relevance of features against the gold labels. 

Created on Nov 9, 2016

@author: lefterav
'''

from ml.lib.orange.ranking import dataset_to_instances
import sys
from Orange.feature.scoring import score_all, InfoGain, GainRatio, Relief, Relevance, Cost, Gini, Distance, MDL

ATTRIBUTE_SET_LIMIT=10
LENGTH_LIMIT=1000

def print_feature_scores(instances, methods):
    for method in methods:
        print method
        scores = score_all(instances, method)
        i = 0
        for score, attribute_name in scores:
            i += 1
            print "%5.3f\t%s" % (score, attribute_name)
            

if __name__ == '__main__':
    filename = sys.argv[1]
    instances = dataset_to_instances(filename, 
                                     attribute_set_limit=ATTRIBUTE_SET_LIMIT, 
                                     length_limit=LENGTH_LIMIT)
    methods = [InfoGain, GainRatio, Relief, Relevance, Cost, Gini, Distance, MDL]
    print_feature_scores(instances, methods)

    
