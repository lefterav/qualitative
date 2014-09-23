'''
Created on Sep 19, 2014

@author: Eleftherios Avramidis
'''

import logging
from ml.lib.orange.ranking import OrangeRanker
#from ml.lib.scikit import ScikitRanker
from expsuite import PyExperimentSuite 

class RankingExperiment(PyExperimentSuite):
    
    restore_supported = True
    
    def reset(self, params, rep):
        self.restore_supported = True
        
        classifier_name = params["classifier"] + "Learner"
        self.learner = eval(classifier_name)
        try:
            self.classifier_params = eval(params["params_{}".format(params["classifier"]).lower()])
        except:
            self.classifier_params = {}
        
        logging.info("Accepted classifier parameters: {}\n".format(self.classifier_params))
        
        self.remove_infinite = False
        self.delay_accuracy =  False
        
        if classifier_name == "SVMEasyLearner":
            self.classifier_params["verbose"] = True
            self.remove_infinite = True
            self.delay_accuracy = True
        
        self.meta_attributes = params["meta_attributes"].split(",")
        self.include_references = params.setdefault("include_references", False)
        self.replacement = params.setdefault("replacement", True)
        self.filter_unassigned = params.setdefault("filter_unassigned", False)
        self.restrict_ranks = params.setdefault("restrict_ranks", [])
        
        self.delay_accuracy = params.setdefault("delay_accuracy", self.delay_accuracy)
        self.remove_infinite = params.setdefault("remove_infinite", False)
        self.nullimputation = params.setdefault("nullimputation", False)
        
        self.invert_ranks = params.setdefault("invert_ranks", False)
        self.evaluation_invert_ranks = params.setdefault("evaluation_invert_ranks", False)
        
        if self.restrict_ranks:
            self.restrict_ranks = self.restrict_ranks.split(",")
        
        source_attributes = params["{}_source".format(params["att"])].split(",")
        target_attributes = params["{}_target".format(params["att"])].split(",")
        general_attributes = params["{}_general".format(params["att"])].split(",")
        
        params["source_attributes"] = source_attributes
        params["target_attributes"] = target_attributes
        params["general_attributes"] = general_attributes
        
        self.active_attributes = []
        if general_attributes != [""]:
            self.active_attributes.extend(general_attributes) #TODOL check whether ps prefix is needed
        if source_attributes != [""]:
            self.active_attributes.extend(["src_{}".format(att) for att in source_attributes])
        if target_attributes != [""]:
            self.active_attributes.extend(["tgt-1_{}".format(att) for att in target_attributes])
            self.active_attributes.extend(["tgt-2_{}".format(att) for att in target_attributes])
        
        if self.active_attributes == [""]:
            self.active_attributes = []
        self.discretization = False
        if params.has_key("discretization"):
            self.discretization = params["discretization"]

        self.hidden_attributes = params["hidden_attributes"].split(",")
        self.discrete_attributes = params["discrete_attributes"].split(",")
 
        self.class_name = params["class_name"]
        self.class_type = params["class_type"]
        
        self.testset = params["test_set"].format(**params)
        self.ties = params["ties"]
    
        self.trainset_filename = "trainset.jcml"
        self.pairwise_trainset_filename = "pairwise_trainset.jcml"
        
        self.testset_filename = "testset.jcml"
        self.pairwise_testset_filename = "pairwise_testset.jcml"
        
        self.trainset_orange_filename = "trainset.tab"
        self.testset_orange_filename = "testset.tab"

        self.localdir = "/local/tmp/elav01/tmp"
    
        self.training_sets = params["training_sets"].format(**params).split(',')
        self.learnerclass = params["learnerclass"]
        self.learner = params["learner"]
        self.reader = params["reader"]
        
    def __init__(self, **kwargs):
        self.params = kwargs
    
    def train(self, params):
        ranker_filename = ""
        ranker = self.learnerclass(**self.params)
        ranker.train(**self.params)
        ranker.dump(ranker_filename)
        
    def evaluate(self):
        test_filename = self.params["test_filename"]
        
    