from ml.ranking import Ranker
from dataprocessor.ce.cejcml import CEJcmlReader

import logging as log
from mlpython.learners.ranking import ListNet
from mlpython.mlproblems.ranking import RankingProblem
import numpy as np
from sentence.ranking import Ranking

def dataset_to_instances(filename, 
                         attribute_set=None,
                         class_name=None,
                         reader=CEJcmlReader,
                         default_value = 0,
                         replace_infinite=False,
                         imputer=True,
                         **kwargs):
    dataset = reader(filename, all_target=True)
    i = 0
    data = []
    for parallelsentence in dataset.get_parallelsentences():
        i += 1
        ranking = Ranking(parallelsentence.get_target_attribute_values(class_name))
        ranking.normalize()
        for rank, translation in zip(ranking, parallelsentence.get_translations()):
            vector = translation.get_vector([])
            data.append([vector, rank, i])
    nparray = np.array(data)
    metadata = {'n_queries' : i}
    return RankingProblem(nparray, metadata)    

def parallelsentence_to_instance(parallelsentence, attribute_set):
    pass

class ListNet(Ranker):
    
    def train(self, dataset_filename, 
              scale=True, 
              feature_selector=None, 
              feature_selection_params={},
              feature_selection_threshold=.25, 
              learning_params={}, 
              optimize=True, 
              optimization_params={}, 
              scorers=['f1_score'],
              attribute_set=None,
              class_name=None,
              metaresults_prefix="./0-",
              **kwargs):
        
        trainset = dataset_to_instances(dataset_filename, attribute_set, class_name, **kwargs)
        self.learner = ListNet(n_stages=10)
        self.attribute_set = attribute_set
        self.class_name = class_name
        log.info("Starting training ListNet")     
        self.learner.train(trainset)
    
    def test(self, input_filename, output_filename, **kwargs):
        testset = dataset_to_instances(input_filename, self.attribute_set, self.class_name, **kwargs)
        outputs, costs = self.learner.test(testset)
        print outputs 
        
    
    def get_model_description(self, basename="model"):
        pass
    
    def get_ranked_sentence(self, parallelsentence):
        pass
    
    
    
    