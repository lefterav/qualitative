'''
@author: lefterav
'''

from sentence.rankhandler import RankHandler 
from featuregenerator.featuregenerator import FeatureGenerator
from featuregenerator.diff_generator import DiffGenerator
from sentence.dataset import DataSet
from io.input.orangereader import OrangeData
 
class Ranker(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, classifier, desired_attributes, meta_attributes):
        '''
        Constructor
        '''
        self.classifier = classifier
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
        
        classified_data = test_data.classify_with(self.classifier)
        parallelsentences = classified_data.get_dataset().get_parallelsentences()
        parallelsentences = rankhandler.get_multiclass_from_pairwise_set(parallelsentences, allow_ties)

        
        print "got %d multiclass after classification" % len(parallelsentences)
        
        return parallelsentences[0]      
 