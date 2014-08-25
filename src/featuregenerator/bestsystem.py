'''
Feature generator that provides the name of the winning system as an attribute

Created on Jun 24, 2011
@author: Eleftherios Avramidis
'''

from featuregenerator import FeatureGenerator

class BestSystemFeatureGenerator(FeatureGenerator):
    '''
    Feature generator that provides as an attribute the name of the winning system 
    @ivar critical_feature: the name of the attribute whose function will judge the winning system
    @type critical_feature: str
    @ivar critical_function: the function that will be used to choose a system upon the given attribute
    @type critical_function: lambda 
    '''


    def __init__(self, critical_feature, critical_function=min):
        '''
        Iniitialize a best system feature generator
        @param critical_feature: the name of the attribute whose function will judge the winning system
        @type critical_feature: str
        @param critical_function: the function that will be used to choose a system upon the given attribute
        @type critical_function: lambda
        '''
        self.critical_feature = critical_feature
        self.critical_function = critical_function
        
    
    def get_features_parallelsentence(self, ps):
        value_per_system = [float(tgt.get_attribute(self.critical_feature)) for tgt in ps.get_translations()]
        f = self.critical_function(value_per_system)
        best_systems = []
        id = 0
        for wer_value in value_per_system:
            id += 1
            if wer_value == f:
                best_systems.append(id)
        if best_systems > 1:
            
            print "maybe more than one best systems according to %s" % self.critical_function.__name__
        
        return {'best': str(best_systems[0])}        