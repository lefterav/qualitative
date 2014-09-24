'''
Created on Sep 19, 2014

@author: Eleftherios Avramidis
'''

import logging
from ml.lib.orange.ranking import OrangeRanker
#from ml.lib.scikit import ScikitRanker
from expsuite import PyExperimentSuite 
from sentence.parallelsentence import AttributeSet
from dataprocessor.ce.utils import join_jcml

class RankingExperiment(PyExperimentSuite):
    
    restore_supported = True
    
    def reset(self, params, rep):
        self.restore_supported = True
        
        try:
            self.learner_params = eval(params["params_{}".format(params["learner"]).lower()])
        except:
            self.learner_params = {}
        
        logging.info("Accepted classifier parameters: {}\n".format(self.learner_params))
        
        self.meta_attributes = params["meta_attributes"].split(",")        
        self.hidden_attributes = params["hidden_attributes"].split(",")
        self.discrete_attributes = params["discrete_attributes"].split(",")
        
        general_attributes = params["{}_general".format(params["att"])].split(",")
        source_attributes = params["{}_source".format(params["att"])].split(",")
        target_attributes = params["{}_target".format(params["att"])].split(",")
        
        self.attribute_set = AttributeSet(general_attributes, source_attributes, target_attributes)
                
        self.training_sets = params["training_sets"].format(**params).split(',')
        self.testsets = params["training_sets"].format(**params).split(',')
                
    def train(self, params):
        params.update(self.learner_params)
        dataset_filename = "trainingset.jcml"
        output_filename = "trainingset.tab" 
        ranker_filename = "ranker.dump"
        
        join_jcml(self.training_sets, dataset_filename)
                                      
        ranker = OrangeRanker(learner=params["learner"])
        ranker.train(dataset_filename = dataset_filename, 
                     output_filename = output_filename,
                     **params)
        
        ranker.dump(ranker_filename)
        
    def evaluate(self):
        test_filename = self.params["test_filename"]
        testset_filename = "testset.jcml"
        output_filename = "testset.tab"
    
    
    def iterate(self, params, rep, n):
        ret = {}
        
        if n==0:
            self.train(params)
        
        
if __name__ == '__main__':
    FORMAT = "%(asctime)-15s [%(process)d:%(thread)d] %(message)s "
    #now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
#    logging.basicConfig(filename='autoranking-{}.log'.format(now),level=logging.DEBUG, format=FORMAT)
#    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.INFO)
#    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
    mysuite = RankingExperiment();
    mysuite.start()