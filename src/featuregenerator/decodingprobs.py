'''
Created on 05.10.2011

@author: elav01
'''
import re
import numpy
from copy import deepcopy
from featuregenerator import FeatureGenerator

class DecodingProbsAnalyzer(FeatureGenerator):
    '''
    It reads and creates meaningful low-level statistics from SMT decoding probabilities.
    The current version reads Joshua and Matrex probabilities and delivers 
    arithmetic mean, standard deviation and variance, for each feature
    It also cleans up the sentence-length-dependent probability attributes
    '''
    
    def add_features_tgt(self, simplesentence, parallelsentence):
        
        simplesentence = deepcopy(simplesentence)

        #this is currently for joshua:
        #Take the log prob differences for every translation step, for every feature
        # after sorting them, and calculate mean, std and var
        tool_id = simplesentence.get_attribute("system")
        
        attributes = simplesentence.get_attributes()
        if (tool_id == "t1"):
            attributes = self.analyze_probs_joshua(attributes)    
        
        elif (tool_id == "t5"):
            attributes = self.analyze_probs_matrex(attributes)
                #TODO: make the names nice, get everything into separate functions and then place them nicely into a dict
        
        simplesentence.attributes = attributes                 
        return simplesentence
    
    def analyze_probs_joshua(self, attributes):
        """
            It receives a dictionary of Joshua decoding probability scores and merges them into three basic ones 
        """
        logp_list = {}
        produced_atts = {}
        todelete = []
        
        #gather all attributes of each feature in one vector, so that basic statistics can be calculated
        for attribute in attributes:
            if attribute.startswith("ds_t1-translogp"):
            	value = float(attributes[attribute])
                (feature_id, phrase_id) = re.findall("ds_t1-translogp(\d*)-(\d*)", attribute)[0]
                if logp_list.has_key(int(feature_id)):
                    logp_list[int(feature_id)][int(phrase_id)] = value
                else:
                    logp_list[int(feature_id)] = {int(phrase_id) : value}
                todelete.append(attribute)
        
        
        for attribute in todelete:
	        del(attributes[attribute])
        
        for feature_id in logp_list:
            feature_steps = logp_list[feature_id]
            diffs = []
            prev_value = 0.00
            for step in sorted(feature_steps.keys())[1:]:
                value = feature_steps[step]
                diff = value - prev_value
                diffs.append(diff)
                prev_value = value
            

            mean = numpy.average(diffs)
            att_name = "%s-mean" % feature_id
            produced_atts[att_name] = str(mean)
            
            std = numpy.std(diffs)
            att_name = "%s-std" % feature_id
            produced_atts[att_name] = str(std)
            
            var = numpy.var(diffs)
            att_name = "%s-var" % feature_id
            produced_atts[att_name] = str(var)
            
        attributes.update(produced_atts)
        
        return attributes
    
    def analyze_probs_matrex(self, attributes):
        logp_list = {}
        produced_atts = {}
        todelete = []
        
        #gather all attributes of each feature in one vector, so that basic statistics can be calculated
        for attribute in attributes:

            if attribute.startswith("ds_t5"):
            	value = float(attributes[attribute])
                (feature_id, phrase_id) = re.findall("ds_t5-([pCc]*)-(\d*)", attribute)[0]
                if logp_list.has_key(feature_id):
                    logp_list[feature_id][int(phrase_id)] = value
                else:
                    logp_list[feature_id] = {int(phrase_id) : value}
                todelete.append(attribute)
        
        for attribute in todelete:
	        del(attributes[attribute])
            
        for feature_id in logp_list:
            feature_steps = logp_list[feature_id]
            
            probs = [feature_steps[step] for step in sorted(feature_steps.keys())]
            
            mean = numpy.average(probs)
            att_name = "%s-mean" % feature_id
            produced_atts[att_name] = str(mean)
            
            std = numpy.std(probs)
            att_name = "%s-std" % feature_id
            produced_atts[att_name] = str(std)
            
            var = numpy.var(probs)
            att_name = "%s-var" % feature_id
            produced_atts[att_name] = str(var)
            
        attributes.update(produced_atts)
        
        return attributes
