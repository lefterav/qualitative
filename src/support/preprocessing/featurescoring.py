'''
Utility script that measures the relevance of features against the gold labels. 

Created on Nov 9, 2016

@author: lefterav
'''

from ml.lib.orange.ranking import dataset_to_instances
import sys
from Orange.feature.scoring import score_all, InfoGain, GainRatio, Relief, Relevance, Cost, Gini, Distance, MDL
from sentence.parallelsentence import AttributeSet

ATTRIBUTE_SET_LIMIT=10
LENGTH_LIMIT=10


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
                   'berkeley-best-parse-confidence_ratio ',
                   'berkeley-n ',
                   'berkeley-n_ratio ',
                   'berkley-loglikelihood ',
                   'berkley-loglikelihood_ratio',
                   'bi-prob',
                   'length ',
                   'length_ratio ',
                   'parse-comma',
                   'parse-comma_ratio ',
                   'parse-dot ',
                   'parse-dot_ratio',
                   'parse-NN',
                   'parse-NN_ratio ',
                   'parse-NP ',
                   'parse-NP_ratio ',
                   'parse-PP',
                   'parse-PP_ratio ',
                   'parse-VB',
                   'parse-VP',
                   'parse-VP_ratio',
                   'prob',
                   'tri-prob ',
                   'uni-prob',
                   'unk ',
                   ]


attributes_set = AttributeSet([], source_features, target_features, [])

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

    
