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
from Orange.orange import VarTypes, Domain
from Orange.data.preprocess import EquiNDiscretization

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
                   #'berkeley-avg-confidence_ratio',
                   'berkeley-best-parse-confidence',
                   #'berkeley-best-parse-confidence_ratio',
                   'berkeley-n',
                   #'berkeley-n_ratio',
                   'berkley-loglikelihood',
                   #'berkley-loglikelihood_ratio',
                   #'bi-prob',
                   'length',
                   #'length_ratio',
                   'parse-comma',
                   #'parse-comma_ratio',
                   'parse-dot',
                   #'parse-dot_ratio',
                   #'parse-NN',
                   #'parse-NN_ratio',
                   'parse-NP',
                   #'parse-NP_ratio',
                   #'parse-PP',
                   #'parse-PP_ratio',
                   #'parse-VB',
                   'parse-VP',
                   #'parse-VP_ratio',
                   'prob',
                   #'tri-prob',
                   #'uni-prob',
                   'unk',
                   ]


attribute_set = AttributeSet([], source_features, target_features, [])

def print_feature_scores(instances, methods):
    for method in methods:
        print method
        # apply the method to all features 
        log.info("Starting scoring with {}".format(method))
        scores = score_all(instances, method)
        log.info("Finished scoring")
        i = 0
        # Filter out nans because they break sorting
        scores = [(a, s) for a, s in scores if not str(s)=='nan']
        for attribute_name, score in sorted(scores, key=lambda s: s[1], reverse=True):
            i += 1
            print "%s\t%5.3f" % (attribute_name, score)


#function copied from rank widget
def get_discretized_data(data, intervals):
    discretizer = EquiNDiscretization(numberOfIntervals=intervals)
    continuous_attributes = filter(lambda attr: attr.varType == VarTypes.Continuous, data.domain.attributes)
    at = []
    attr_dict = {}
    for attri in continuous_attributes:
        try:
            nattr = discretizer(attri, data)
            at.append(nattr)
            attr_dict[attri] = nattr
        except:
            pass
    discretized_data = data.select(Domain(at, data.domain.classVar))
    discretized_data.setattr("attr_dict", attr_dict)
    return discretized_data


if __name__ == '__main__':
    filename = sys.argv[1]

    log.basicConfig(level=log.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    instances = dataset_to_instances(filename, 
                                     attribute_set=attribute_set,
                                     attribute_set_limit=ATTRIBUTE_SET_LIMIT, 
                                     replace_infinite=True,
                                     replace_nan=True,
                                     default_value=0,
                                     length_limit=LENGTH_LIMIT,
                                     class_name='rank')
    log.info("Finished dataset conversion")
    
    # first score with the methods working on continuous features
    continuous_methods = [Relief, MDL]
    print_feature_scores(instances, continuous_methods)
    
    # the score with the methods working only on discrete features
    discrete_methods = [InfoGain, Relevance, Gini, Distance]
    discrete_instances = get_discretized_data(instances, 100)
    print_feature_scores(discrete_instances, discrete_methods)

    
