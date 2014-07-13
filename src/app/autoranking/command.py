'''
Created on Jun 21, 2013

@author: Eleftherios Avramidis
'''

from sentence.dataset import DataSet
from sentence.pairwisedataset import AnalyticPairwiseDataset
from classifier.orange import OrangeClassifier
import cPickle as pickle

class SimpleAutoranking:
    def init(self, **params):
        params = _read(config_filename)
        self.restore_supported = True
        
        self.remove_infinite = False
        
        self.meta_attributes = params["meta_attributes"].split(",")
        self.include_references = params.setdefault("include_references", False)
        self.replacement = params.setdefault("replacement", True)
        self.filter_unassigned = params.setdefault("filter_unassigned", False)
        self.restrict_ranks = params.setdefault("restrict_ranks", [])
        
        self.delay_accuracy = params.setdefault("delay_accuracy", False)
        self.remove_infinite = params.setdefault("remove_infinite", False)
        
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
        
        objectfile = open(params["trained_classifier"], 'r')
        self.classifier = OrangeClassifier(pickle.load(objectfile))
        objectfile.close()
    
    def run(self, parallelsentence):
        self.testset = DataSet([parallelsentence])
        self.testset = AnalyticPairwiseDataset(self.testset, replacement = self.replacement, rankless=True)
        
    
    

if __name__ == '__main__':
    pass