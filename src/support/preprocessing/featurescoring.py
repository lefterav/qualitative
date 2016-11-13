'''
Utility script that measures the relevance of features against the gold labels. 

Created on Nov 9, 2016

@author: lefterav
'''

from ml.lib.orange.ranking import dataset_to_instances
import sys
from Orange.feature.scoring import score_all, InfoGain, GainRatio, Relief, Relevance, Cost, Gini, Distance, MDL
from sentence.parallelsentence import AttributeSet
from operator import itemgetter
import logging as log

ATTRIBUTE_SET_LIMIT=10
LENGTH_LIMIT=None


source_features = ['berkeley-avg-confidence',
                   'berkeley-best-parse-confidence',
                   'berkeley-n',
                   'berkley-loglikelihood',
                   'length',
                   'parse-comma', 
                   'parse-dot', 
                   'parse-NN', 
                   'parse-NP',
                   'parse-PP',
                   'parse-VP',
                   'parse-VVFIN',
                   ]

target_features = ['berkeley-avg-confidence',
                   'berkeley-avg-confidence_ratio',
                   'berkeley-best-parse-confidence',
                   'berkeley-best-parse-confidence_ratio',
                   'berkeley-n',
                   'berkeley-n_ratio',
                   'berkley-loglikelihood',
                   'berkley-loglikelihood_ratio',
                   'bi-prob',
                   'length',
                   'length_ratio',
                   'parse-comma',
                   'parse-comma_ratio',
                   'parse-dot',
                   'parse-dot_ratio',
                   'parse-NN',
                   'parse-NN_ratio',
                   'parse-NP',
                   'parse-NP_ratio',
                   'parse-PP',
                   'parse-PP_ratio',
                   'parse-VB',
                   'parse-VP',
                   'parse-VP_ratio',
                   'prob',
                   'tri-prob',
                   'uni-prob',
                   'unk',
                   ]


attribute_set = AttributeSet([], source_features, target_features, [])

def print_feature_scores(instances, methods):
    for method in methods:
        print method
        log.info("Starting scoring")
        scores = score_all(instances, method)
        log.info("Finished scoring")
        i = 0
        scores = [s for s in scores if not str(s[1])=='nan']
        for attribute_name, score in sorted(scores, key=lambda s: abs(s[1]), reverse=True):
            i += 1
            print "%5.3f\t%s" % (score, attribute_name)
            

if __name__ == '__main__':
    filename = sys.argv[1]
    instances = dataset_to_instances(filename, 
                                     attribute_set=attribute_set,
                                     attribute_set_limit=ATTRIBUTE_SET_LIMIT, 
                                     length_limit=LENGTH_LIMIT,
                                     class_name='rank')
    log.info("Finished dataset conversion")
    methods = [Relief, InfoGain]
#, Relevance, Cost, Gini, Distance, MDL]
    print_feature_scores(instances, methods)

    
