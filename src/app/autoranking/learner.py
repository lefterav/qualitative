'''
Created on Sep 19, 2014

@author: Eleftherios Avramidis
'''

import logging
from collections import OrderedDict
from ml.lib.orange.ranking import OrangeRanker
#from ml.lib.scikit import ScikitRanker
from expsuite import PyExperimentSuite 
from sentence.parallelsentence import AttributeSet
from sentence.scoring import Scoring
from dataprocessor.ce.utils import join_jcml
from dataprocessor.ce.cejcml import CEJcmlReader

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
        
        self.attribute_set = self._read_attributeset(params)
                
        self.training_sets = params["training_sets"].format(**params).split(',')
        self.testsets = params["training_sets"].format(**params).split(',')
    
    
    def _read_attributeset(self, params):
        general_attributes = self._read_attributes(params, "general")
        source_attributes = self._read_attributes(params, "source")
        target_attributes = self._read_attributes(params, "target")    
        attribute_set = AttributeSet(general_attributes, source_attributes, target_attributes)
        return attribute_set
    
    def _read_attributes(self, params, key):
        attset = params["att"]
        attribute_key = "{}_{}".format(attset, key)
        attribute_names = params.setdefault(attribute_key, [])
        #print attribute_key
        #print attribute_names
        #print type(attribute_names)
        if attribute_names:
            attribute_names = attribute_names.split(',')
        else:
            attribute_names = []
        #print attribute_names
        return attribute_names
    
                
                
                
                
    def train(self, params):
        """
        Load training data and train new ranking model
        """
        logging.info("Started training")
        params.update(self.learner_params)
        params["attribute_set"] = self.attribute_set
        
        logging.info("train: Attribute_set before training: {}".format(params["attribute_set"]))
        
        dataset_filename = "trainingset.jcml"
        output_filename = "trainingset.tab" 
        ranker_filename = "ranker.dump"
        
        logging.info("Joining training files")
        join_jcml(self.training_sets, dataset_filename)
                                      
        logging.info("Launching ranker based on {}".format(params["learner"]))                                                
        ranker = OrangeRanker(learner=params["learner"])
        ranker.train(dataset_filename = dataset_filename, 
                     output_filename = output_filename,
                     **params)
        
        ranker.dump(ranker_filename)
        
        logging.info("Extracting fitted coefficients")
        model_description = ranker.get_model_description()
        
        return model_description
        

    def test(self, params):
        """
        Load test set and apply machine learning to assign labels
        """
        testset_input = self.testsets[0]
        testset_output = "testset_annotated.jcml"
        ranker = OrangeRanker(filename="ranker.dump")
        return ranker.test(testset_input, testset_output)
    
    
    def evaluate(self, params):
        """
        Load predictions (test) and analyze performance
        """
        testset_output = "testset_annotated.jcml"
        testset = CEJcmlReader(testset_output, all_general=True, all_target=True).get_dataset(compact=True)
        
        class_name = params["class_name"]
        
        scores = score(testset, class_name, "rank", "rank_hard", invert_ranks=False)
        return scores
    
    def iterate(self, params, rep, n):
        ret = OrderedDict()
        logging.info("Iteration {}".format(n))
        if n==1:
            ret.update(self.train(params))
        if n==2:
            ret.update(self.test(params))
        if n==3:
            ret.update(self.evaluate(params))
        print ret
        return ret
    

def get_scoring(testset, class_name, xid, featurename):
    scoringset = Scoring(testset)
    ret = {}
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid)))
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid), suffix="-ntp", exclude_ties=False))
    ret.update(scoringset.get_kendall_tau(featurename, class_name, prefix="{}-".format(xid), suffix="-nt", penalize_predicted_ties=False))
#    ret["mrr"] = scoringset.mrr(featurename, class_name)
    ret["kendalltau_b-%s"%xid], ret["kendalltau_b-%s-pi"%xid]  = scoringset.get_kendall_tau_b(featurename, class_name)
    ret["b1-acc-1-%s"%xid], ret["b1-acc-%s-any"%xid] = scoringset.selectbest_accuracy(featurename, class_name)
    ret["fr-%s"%xid] = scoringset.avg_first_ranked(featurename, class_name)    
    ret["pr-%s"%xid] = scoringset.avg_predicted_ranked(featurename, class_name)
    
    sb_percentages = scoringset.best_predicted_vs_human(featurename, class_name)  
    for rank, percentage in sb_percentages.iteritems():
        ret["sb-{}-{}".format(rank,xid)] = str(percentage)
    return ret

def score(testset, class_name, xid, featurename, invert_ranks=False):
    scoringset = Scoring(testset, invert_ranks=invert_ranks)
    return scoringset.get_metrics_scores(featurename, class_name, prefix=xid)
      
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
    
    # define a Handler which writes INFO messages or higher to the sys.stderr
    #console = logging.StreamHandler()
    #console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    #formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    #console.setFormatter(formatter)
    # add the handler to the root logger
    #logging.getLogger('').addHandler(console)
    FORMAT = "%(asctime)-15s [%(process)d:%(thread)d] %(message)s "
    #now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
#    logging.basicConfig(filename='autoranking-{}.log'.format(now),level=logging.DEBUG, format=FORMAT)
#    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.INFO)
#    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
    mysuite = RankingExperiment();
    
    mysuite.start()