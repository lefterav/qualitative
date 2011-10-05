'''
Created on 05.10.2011

@author: elav01
'''
import re
import numpy

class DecodingProbsProcessor(object):
    '''
    It reads and creates meaningful low-level statistics from SMT decoding probabilities.
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
    
    def get_features_tgt(self, simplesentence, parallelsentence):
        
        logp_list = {}
        
        #this is currently for joshua:
        #Take the log prob differences for every translation step, for every feature
        # after sorting them, and calculate mean, std and var
        tool_id = simplesentence.get_attributes("tool_id")
        if (tool_id == "t1"):
            for attribute in simplesentence.get_attributes():
                if attribute.startswith("ds_t1-translogp"):
                    (feature_id, phrase_id) = re.findall("ds_t1-translogp(\d*)-(\d*)", attribute)
                    if logp_list.has_key(feature_id):
                        logp_list[int(feature_id)][int(phrase_id)] = float(attribute.value)
                    else:
                        logp_list[int(feature_id)] = {int(phrase_id) : float(attribute.value)}
                      
        
            for feature_id in logp_list:
                feature_steps = logp_list[feature_id]
                diffs = []
                prev_value = 0.00
                for step in sorted(feature_steps.keys())[1:]:
                    value = step.value
                    diff = value - prev_value
                    diffs.append(diff)
                    prev_value = value
                 
                mean = numpy.average(diff)
                std = numpy.std(diff)
                var = numpy.var(diff)
        
        elif (tool_id == "t5"):
            for attribute in simplesentence.get_attributes():

                if attribute.startswith("ds_t5"):
                    (feature_id, phrase_id) = re.findall("ds_t5-([pCc]*)-(\d*)", attribute)
                    if logp_list.has_key(feature_id):
                        logp_list[feature_id][int(phrase_id)] = float(attribute.value)
                    else:
                        logp_list[feature_id] = {int(phrase_id) : float(attribute.value)}
            
            for feature_id in logp_list:
                feature_steps = logp_list[feature_id]
                
                probs = [step.value for step in sorted(feature_steps.keys())]
                 
                mean = numpy.average(probs)
                std = numpy.std(probs)
                var = numpy.var(probs)
                #TODO: make the names nice, get everything into separate functions and then place them nicely into a dict
            
                     
            
                
        return None
    
        