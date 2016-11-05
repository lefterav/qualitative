'''
@author: Eleftherios Avramidis
'''

from sentence.rankhandler import RankHandler 
from featuregenerator import FeatureGenerator
from featuregenerator.diff_generator import DiffGenerator
from sentence.dataset import DataSet
from dataprocessor.input.orangereader import OrangeData
 
class PairwiseRanker(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, learner, desired_attributes, meta_attributes):
        '''
        Constructor
        '''
        self.learner = learner
        self.desired_attributes = desired_attributes
        self.meta_attributes = meta_attributes
        
    

    def add_features_parallelsentence(self, parallelsentence, apply_diff = True):
        rankhandler = RankHandler()
        allow_ties = False
        parallelsentences = rankhandler.get_pairwise_from_multiclass_set([parallelsentence], allow_ties)
        
        try:
            print parallelsentence.get_attribute("id")
        except:
            pass
        
        if apply_diff: 
            dg = DiffGenerator()
        
            parallelsentences = [dg.add_features_parallelsentence(parallelsentence) for parallelsentence in parallelsentences]
        
        dataset = DataSet(parallelsentences)
        
        class_name = "rank"
        test_data = OrangeData(dataset, class_name, self.desired_attributes, self.meta_attributes)
        
        classified_data = test_data.classify_with(self.learner)
        parallelsentences = classified_data.get_dataset().get_parallelsentences()
        parallelsentences = rankhandler.get_multiclass_from_pairwise_set(parallelsentences, allow_ties)

        
        print "got %d multiclass after classification" % len(parallelsentences)
        
        return parallelsentences[0]      
 