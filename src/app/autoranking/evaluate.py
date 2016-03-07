'''
Created on 26 Feb 2016

@author: elav01
'''

import logging
from dataprocessor.ce.cejcml import CEJcmlReader
from sentence import scoring
import sys

def evaluate(filename, metric="rank_hard", prefix="hard", class_name = "rank"):
        """
        Load predictions (test) and analyze performance
        """        
        testset = CEJcmlReader(filename, all_general=True, all_target=True)        
        scores = scoring.get_metrics_scores(testset, metric, class_name , prefix=prefix, invert_ranks=False)        
        return scores

if __name__ == '__main__':   
    scores = evaluate(sys.argv[1], metric=sys.argv[2])
    
    print "\n".join(["{}\t{}".format(k, v) for k, v in scores.iteritems()])