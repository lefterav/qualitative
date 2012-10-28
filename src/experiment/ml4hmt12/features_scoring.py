'''
Created on Oct 28, 2012

@author: Eleftherios Avramidis
'''

import Orange
import sys

data = Orange.data.Table(sys.argv[1])
scores = [Orange.feature.scoring.Relief(),
          Orange.feature.scoring.InfoGain(),
          Orange.feature.scoring.GainRatio(),
          Orange.feature.scoring.Gini(),
          Orange.feature.scoring.Relevance(),
          Orange.feature.scoring.Cost(),
          Orange.feature.scoring.Distance(),
          Orange.feature.scoring.MDL()]


if __name__ == '__main__':
    print 'Feature scores for best three features (with score_all):'
    
    for feature in data.domain.features:
        print "{}\t".format(feature.name)
        for score in scores:
            print "{}\t".format(score(feature, data)),
        print
    
            
            
        
    
    
