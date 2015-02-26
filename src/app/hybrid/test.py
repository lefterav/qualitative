'''
Created on 15 Feb 2015

@author: lefterav
'''
import cPickle as pickle
import sys
import logging
from evaluation.selection.set import evaluate_selection
from dataprocessor.ce.cejcml import CEJcmlReader


class HybridTranslator:
    
    def __init__(self, model_filename):
        self.ranker = pickle.load(open(model_filename))
    
    def rank_annotated_batch(self, testset_input_filename, testset_output_filename, target_language, **params):
        function = max 
        mode = params.setdefault("mode", "soft")
        self.ranker.test(testset_input_filename, "{}.jcml".format(testset_output_filename), reconstruct=mode, new_rank_name='rank_{}'.format(mode), **params)
        testset = CEJcmlReader("{}.jcml".format(testset_output_filename, all_general=True, all_target=True))
        refscores_soft = evaluate_selection(testset.get_parallelsentences(),
                                            rank_name="rank_soft",
                                            out_filename="{}.soft.sel.txt".format(testset_output_filename),
                                            ref_filename="{}.ref.txt".format(testset_output_filename),
                                            language=target_language,
                                            function=function
                                            )
        
    

if __name__ == "__main__":

    #loglevel = logging.INFO
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, 
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M')


    model_filename = sys.argv[1]
    testset_input_filename = sys.argv[2]
    testset_output_filename = sys.argv[3]
    target_language = sys.argv[4]
    
    ranker = HybridTranslator(model_filename)
    ranker.rank_annotated_batch(testset_input_filename, testset_output_filename, target_language)
    
    
