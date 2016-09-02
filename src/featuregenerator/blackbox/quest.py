'''
Created on 2 Sep 2016

@author: elav01
'''
from featuregenerator import FeatureGenerator

class QuestSubstitutes(FeatureGenerator):
    '''
    A class that just replicates existing features, by setting the names
    used by Quest for these 
    '''
    #TODO: feature 1013 with ngram perplexities
    mapping = [("q_1002_1" , "l_tokens"), 
    ("q_1003_1", "l_srctokens_ratio"), #needed
    ("q_1004_1", "l_tokens_ratio"), #needed
    ("q_1012_1", "lm_prob"), #maybe 3-gram needed?
    ("q_1015_1", "l_avgoccurences"), 
    ("q_1064_1", "p_commas_diff"),
    ("q_1079_1", "l_numbers_diff_norm"),
    ("q_1081_1", "l_non_aztokens_per"),
    ("q_1082_1", "l_aztokens_ratio"),
    ]
    
    feature_names = [f for f, _ in mapping]
    requirements = [r for _,r in mapping]

    def get_features_tgt(self, simplesentence, parallelsentence):
        attributes = {}
        for new_feature, existing_feature in self.mapping:
            attributes[new_feature] = simplesentence.get_attribute(existing_feature)
        return attributes

        
