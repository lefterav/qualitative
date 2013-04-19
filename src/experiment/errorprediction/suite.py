'''
Implementation of the Python Experiment Suite for the Error Prediction experiment
Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''

from ml import classifier


def _read_attributes(params):
    """
    Helper function to read attribute sets and attributes from configuration file
    @param params: the entire dict of local params
    @type params: dict
    @return: a list with the names of the active attributes
    @rtype: list of strings
    """
    source_attributes = params["{}_source".format(params["att"])].split(",")
    target_attributes = params["{}_target".format(params["att"])].split(",")
    general_attributes = params["{}_general".format(params["att"])].split(",")
        
    active_attributes = []
    if general_attributes != [""]:
        active_attributes.extend(general_attributes) #TODOL check whether ps prefix is needed
    if source_attributes != [""]:
        active_attributes.extend(["src_{}".format(att) for att in source_attributes])
    if target_attributes != [""]:
        active_attributes.extend(["tgt-1_{}".format(att) for att in target_attributes])
        active_attributes.extend(["tgt-2_{}".format(att) for att in target_attributes])
    
    if active_attributes == [""]:
        active_attributes = []
    return active_attributes



class ErrorPredictionSuite(object):
    restore_supported = True
    
    def reset(self, params, rep):
        self.restore_supported = True
        
        #define learner
        learner_name = params["classifier"]
        learner_params = "params_{}".format(learner_name)
        self.learner_params = params.setdefault(learner_params, {})
        self.learner = classifier.forname(learner_name, **self.classifier_params)
        
        #set attributes values
        self.meta_attributes = params["meta_attributes"].split(",")
        self.active_attributes = _read_attributes(params)
        
        self.class_name = params["class_name"]
        self.class_type = params["class_type"]
        
        self.training_sets = params["training_sets"].format(**params).split(',')
        self.testset = params["test_set"].format(**params)
        
        
         