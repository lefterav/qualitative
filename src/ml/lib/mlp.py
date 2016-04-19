from ml.ranking import Ranker
from dataprocessor.ce.cejcml import CEJcmlReader

import logging as log
from mlpython.learners.ranking import ListNet
from mlpython.mlproblems.ranking import RankingProblem
import numpy as np
from sentence.ranking import Ranking
from mlpython.mlproblems.generic import SubsetProblem
from copy import deepcopy

def dataset_to_instances(filename, 
                         attribute_set=None,
                         class_name="rank",
                         reader=CEJcmlReader,
                         default_value = 0,
                         replace_infinite=False,
                         imputer=True,
                         invert_ranks=False,
                         **kwargs):

    dataset = reader(filename, all_target=True)    
    
    if attribute_set == None:
        attribute_set = dataset.get_attribute_set()
    par_attnames = attribute_set.parallel_attribute_names
    src_attnames = attribute_set.source_attribute_names
    tgt_attnames = attribute_set.target_attribute_names

    i = 0
    data = []
    ranks = set()
    skipped = []
    
    #iterate for each parallel sentence in the data
    for parallelsentence in dataset.get_parallelsentences():
        i += 1
        #try:
        ranking = Ranking(parallelsentence.get_target_attribute_values(class_name))
        #except KeyError:
            #if rank is missing, skip this parallelsentence I guess
        #    skipped.append(parallelsentence.get_id())
        #    continue
        # for rank, levenstein distance etc needs to be reversed, cause normally RankList works with scores 
        if not invert_ranks:
            ranking = ranking.normalize().inverse().integers()
        # for BLEU, METEOR and other metrics needs not be reversed
        else:
            ranking = ranking.normalize().integers()
        lengths = []
        
        #get all attributes from parallel sentence
        parallel_vector = parallelsentence.get_vector(par_attnames, 
                                                      default_value=0, 
                                                      replace_infinite=True,
                                                      replace_nan=True)
        
        #get all attributes from source sentence
        source_vector = parallelsentence.get_source().get_vector(
                                                                 src_attnames, 
                                                                 default_value=0, 
                                                                 replace_infinite=True,
                                                                 replace_nan=True)
        
        #iterate for all translations of this parallel sentence
        #and a get one row for each
        for rank, translation in zip(ranking, parallelsentence.get_translations()):
            vector = []
            vector.extend(parallel_vector)
            vector.extend(source_vector)
             
            #get all target attributes
            target_vector = translation.get_vector(tgt_attnames, 
                                                  default_value=0,
                                                  replace_infinite=True,
                                                  replace_nan=True)
            vector.extend(target_vector)
            #gather the lengths of the attributes
            lengths.append(len(vector))
            #gather the rank vectors in the required format
            data.append([np.array(vector), rank, i])
            #gather the possible rank values
            ranks.add(rank)
            
    if len(skipped) > 0:
        log.warning("Conversion from rankings to MLPython structures failed to convert {} rankings: {}".format(len(skipped), skipped))
    max_len = max(lengths)
    data = np.array(data)
    metadata = {'input_size' : max_len, #size of feature vector
                'scores' :  ranks}      #seen rank values
    open("/tmp/filename.np", 'w').write(str(data))
    problemdata = RankingProblem(data, metadata)
    return problemdata    

def parallelsentence_to_instance(parallelsentence, attribute_set,
                                 invert_ranks=False,
                                 class_name="rank"):
    par_attnames = attribute_set.parallel_attribute_names
    src_attnames = attribute_set.source_attribute_names
    tgt_attnames = attribute_set.target_attribute_names
    ranking = Ranking(parallelsentence.get_target_attribute_values(class_name))
    # needs to be reversed, cause normally RankList works with scores 
    if not invert_ranks:
        ranking = ranking.normalize().inverse().integers()
        # for BLEU, METEOR and other metrics needs not be reversed
    else:
        ranking = ranking.normalize().integers()
    lengths = []
    
    #get all attributes from parallel sentence
    parallel_vector = parallelsentence.get_vector(par_attnames, 
                                                  default_value=0, 
                                                  replace_infinite=True,
                                                  replace_nan=True)
    
    #get all attributes from source sentence
    source_vector = parallelsentence.get_source().get_vector(
                                                             src_attnames, 
                                                             default_value=0, 
                                                             replace_infinite=True,
                                                             replace_nan=True)
    
    ranks = set()
    data = []
    #iterate for all translations of this parallel sentence
    #and a get one row for each
    for rank, translation in zip(ranking, parallelsentence.get_translations()):
        vector = []
        vector.extend(parallel_vector)
        vector.extend(source_vector)
         
        #get all target attributes
        target_vector = translation.get_vector(tgt_attnames, 
                                              default_value=0,
                                              replace_infinite=True,
                                              replace_nan=True)
        vector.extend(target_vector)
        #gather the lengths of the attributes
        lengths.append(len(vector))
        #gather the rank vectors in the required format
        data.append([np.array(vector), rank, 0])
        #gather the possible rank values
        ranks.add(rank)
    max_len = max(lengths)
    data = np.array(data)
    metadata = {'input_size' : max_len, #size of feature vector
                'scores' :  ranks} 
    return RankingProblem(data, metadata)

class ListNetRanker(Ranker):
   
    def initialize(self):
        assert ("ListNet" in self.name)
        log.info("Initialized ListNet")

    def train(self, dataset_filename, 
              #scale=True, 
              #feature_selector=None, 
              #feature_selection_params={},
              #feature_selection_threshold=.25, 
              #learning_params={}, 
              #optimize=True, 
              #optimization_params={}, 
              #scorers=['f1_score'],
              attribute_set=None,
              class_name="rank",
              #metaresults_prefix="./0-",
              reader=CEJcmlReader,
              n_stages=200,
              hidden_size=50, learning_rate=0.01, weight_per_query=False, alpha=1.0,
              invert_ranks=False,
              **kwargs):

        #remember whether ranks have been inverted during training, cause they have to be inverted on testing too
        self.invert_ranks = invert_ranks
        
        #attribute set cannot be None, cause we have to conform the test set
        #to the same structure
        if attribute_set == None:
            dataset = reader(dataset_filename, all_target=True)    
            attribute_set = dataset.get_attribute_set()
        self.attribute_set = attribute_set
        self.class_name = class_name
        
        #initialize the learner class
        self.learner = ListNet(n_stages, hidden_size, learning_rate, weight_per_query, alpha)
        #convert all the dataset to the batch format that ListNet expects
        trainset = dataset_to_instances(dataset_filename, self.attribute_set, 
                                        class_name, reader=reader, invert_ranks=invert_ranks, 
                                        **kwargs)
        self.attribute_set = attribute_set
        self.class_name = class_name
        log.info("Starting training ListNetRanker")     
        self.learner.train(trainset)
        self.fit = True
        log.info("ListNetRanker training finished")     
        
        #store a single-instance set as a class variable
        #so that it can be served for restructuring future training sets
        sample_data, sample_metadata = trainset.raw_source()
        sample_data = SubsetProblem(sample_data, subset=set([0]))
        self.data_structure = RankingProblem(sample_data, sample_metadata)
        return {}
    
    def _get_first_instance(self, sample_data):
        """
        Get the first item of the ranked data
        """
        new_sample_data = []
        for vector, rank, query in sample_data:
            if query == 0:
                new_sample_data.append([vector, rank, query])
            else:
                return new_sample_data     
       
    
    def get_model_description(self, basename="model"):
        l = self.learner
        description = {"param_n_stages" : l.n_stages,
                       "param_hidden_size" : l.hidden_size,
                       "param_learning_rate" : l.learning_rate,
                       "param_weight_per_query" : l.weight_per_query,
                       "param_alpha" : l.alpha,
                       "param_merge_document_and_query" : l.merge_document_and_query,
                       "param_seed" : l.seed,
#                       "rng": l.rng,
                       "max_score": l.max_score,
#                       "V": l.V,
#                       "c": l.c,
#                       "W": l.W,
#                       "b": l.b
                       }
        return description
            
    
    def get_ranked_sentence(self, parallelsentence, 
                            new_rank_name="rank_hard", **kwargs):
        #convert the parallelsentence into the structure accepted by ListNet
        instance = parallelsentence_to_instance(parallelsentence, 
                                                self.attribute_set, 
                                                self.class_name)
        #conform the instance structure to the one of the training set
        instance = self.data_structure.apply_on(instance.data, 
                                                instance.metadata)
        ranking = self.learner.use(instance)[0]
        # if we reversed ranks on training (rank, levenshtein) order stays the same
        if not invert_ranks:
            ranking = ranking.normalize().integers()
        # otherwise for BLEU, METEOR and other metrics needs to be reversed
        # cause we will evaluate against BLEU or METEOR
        else:
            ranking = ranking.normalize().inverse().integers()
 
        ranked_parallelesentence = deepcopy(parallelsentence)
        for simplesentence, new_rank in zip(ranked_parallelesentence.tgt, ranking):
            simplesentence.attributes[new_rank_name] = new_rank
        return ranked_parallelesentence, None
