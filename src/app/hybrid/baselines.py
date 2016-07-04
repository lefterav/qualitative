'''
Created on Jul 3, 2016

@author: lefterav
'''
from app.hybrid.learn import RankingExperiment
from collections import OrderedDict
import logging
import os
import sys
from dataprocessor.ce.cejcml import CEJcmlReader
from sentence import scoring

class BaseLineSimulation(RankingExperiment):
    '''
    Calculate Baseline and Metric scores for the same settings as another experiments
    '''

    restore_supported = True
    def __init__(self):
        # Allow restoring pipeline
        self.restore_supported = True
        # Initialize superclass from Experiment Suite
        super(BaseLineSimulation, self).__init__()

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
        logging.info("Class name: {}".format(class_name))
        
        #empty ordered dict to load scores
        scores = OrderedDict()
        
        for testset_filename in self.testset_filenames:
            #measure ranking scores for soft recomposition
            testset = CEJcmlReader(testset_filename, all_general=True, all_target=True) 
            logging.debug("The testset file to be opened is: {}".format(testset_filename))
            baseline_scores = scoring.get_baseline_scores(testset, class_name , prefix="base_", invert_ranks=self.invert_ranks)
            scores.update(baseline_scores)
        return scores

    def reset(self, params, rep):
        logging.info("Running in {}".format(os.getcwd()))
        #TODO: find a more safe way to decide when to invert ranks
        self.invert_ranks = False


if __name__ == '__main__':
    loglevel = logging.INFO
    if "--debug" in sys.argv:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

    FORMAT = "%(asctime)-15s [%(process)d:%(thread)d] %(message)s "

    mysuite = BaseLineSimulation();
    
    mysuite.start()
    logging.info("Done!") 
