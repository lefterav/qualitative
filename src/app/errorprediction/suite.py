'''
Implementation of the Python Experiment Suite for the Error Prediction app
Created on 19 Apr 2013

@author: Eleftherios Avramidis
'''

from ml import classifier
import logging

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
    
        self.training_jcml = "training.jcml"
        
    
    def iterate(self, params, rep, n):
        ret = {}
        
        from dataprocessor.input.jcmlreader import JcmlReader
        from dataprocessor.sax.saxps2jcml import IncrementalJcml
        
        
        if n == 0:
            logging.info("fetch training set")

            xmlfile = IncrementalJcml(self.training_jcml)
            for training_set in self.training_sets:
                for parallelsentence in JcmlReader(training_set).get_parallelsentences():
                    xmlfile.add_parallelsentence(parallelsentence)
            xmlfile.close()
        
        if n == 20:
            logging.info("convert data")
            self.learner.set_training_data(self.training_jcml, 
                  self.class_name, 
                  self.desired_attributes,
                  self.meta_attributes,
                  get_nested_attributes=True,
                  remove_infinite=self.remove_infinite
                  )
        if n == 40:
            logging.info("train model")
            self.learner.load_training_data()
            self.learner.train()
            self.learner.write_model_description()
            self.learner.unload()
        
        if n == 60:
            logging.info("score learner")
            ret = self.cross_validation_scores()
        return ret
    
    def restore_state(self, params, rep, n):
        #no variables to restore, everything done in files
        pass
        
            
        
                    
