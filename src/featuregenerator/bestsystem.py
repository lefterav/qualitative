'''
Created on Jun 24, 2011

@author: Eleftherios Avramidis
'''

from featuregenerator import FeatureGenerator

class BestSystemFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, critical_feature, critical_function):
        '''
        Constructor
        '''
        self.critical_feature = critical_feature
        self.critical_function = critical_function
        
    
    def get_features_parallelsentence(self, ps):
        value_per_system = [float(tgt.get_attribute(self.critical_feature)) for tgt in ps.get_translations()]
        min_wer = min(value_per_system)
        best_systems = []
        id = 0
        for wer_value in value_per_system:
            id += 1
            if wer_value == min_wer:
                best_systems.append(id)
        if best_systems > 1:
            
            print "maybe more than one best systems according to %s" % self.critical_function.__class__.__name__
        
        return {'best': str(best_systems[0])}
            
        

            
        