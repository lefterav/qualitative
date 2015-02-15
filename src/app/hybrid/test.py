'''
Created on 15 Feb 2015

@author: lefterav
'''
import cPickle as pickle
import sys

class HybridTranslator:
    
    def __init__(self, model_filename):
        self.ranker = pickle.load(open(model_filename))
    
    def rank_annotated_batch(self, testset_input_filename, testset_output_filename, **params):
        
        mode = params.setdefault("mode", "soft")
        self.ranker.test(testset_input_filename, testset_output_filename, reconstruct=mode, new_rank_name='rank_{}'.format(mode), **params)
    
        return {}
    

if __name__ == "__main__":
    model_filename = sys.argv[1]
    testset_input_filename = sys.argv[2]
    testset_output_filename = sys.argv[2]
    
    ranker = HybridTranslator(model_filename)
    ranker.rank_annotated_batch(testset_input_filename, testset_output_filename)
    
    