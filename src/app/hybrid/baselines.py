'''
Created on Jul 3, 2016

@author: lefterav
'''
from app.hybrid.learn import RankingExperiment
from collections import OrderedDict
import logging
import os
from dataprocessor.ce.cejcml import CEJcmlReader
from sentence import scoring

class BaseLineSimulation(RankingExperiment):
    '''
    Calculate Baseline and Metric scores for the same settings as another experiments
    '''

    def iterate(self, params, rep, n):
        ret = OrderedDict()
        logging.info("Running in {}".format(os.getcwd()))
        logging.info("Repetition: {}, Iteration: {}".format(rep, n))
        if n==0:
            self.prepare_data(params, rep)
        elif n==5:
            self.evaluate_baseline(params, rep)
        return ret
    
    def evaluate_baseline(self, params, rep):
        """
        Load predictions (test) and analyze performance
        """
        class_name = params["class_name"]
        
        #empty ordered dict to load scores
        scores = OrderedDict()
        
        #@TODO: wmt ranks are none
        for testset_filename in enumerate(self.testset_filenames):
            #measure ranking scores for soft recomposition
            testset = CEJcmlReader(testset_filename, all_general=True, all_target=True) 
            baseline_scores = scoring.get_baseline_scores(testset, class_name , prefix="base_", invert_ranks=self.invert_ranks)
            scores.update(baseline_scores)
        return scores 