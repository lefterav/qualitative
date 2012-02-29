'''
Created on 23 Feb 2012

@author: lefterav
'''

from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet
from io.sax.saxps2jcml import Parallelsentence2Jcml
from orange import BayesLearner 
from classifier.classifier import OrangeClassifier


if __name__ == '__main__':
    
    input_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.jcml"
    output_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.coupled.jcml"
    
    print "loading big set"
    simple_dataset = JcmlReader(input_file).get_dataset() 
    
    print "spliting set"
    simple_dataset, a = simple_dataset.split(0.05)
    
    Parallelsentence2Jcml(simple_dataset.get_parallelsentences()).write_to_file('/home/elav01/taraxu_data/wmt12/qe/training_set/training-sample.jcml')
    simple_trainset, simple_testset = simple_dataset.split(0.9)
    simple_dataset = None
    
    print "coupling training set"
    coupled_trainset = CoupledDataSet(simple_trainset)
    simple_trainset = None
    print "orange version of coupling training set"
    
    meta_attributes = ["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", "ps1_id", "ps2_id", "tgt-1_score" , "tgt-2_score", "tgt-1_system" , "tgt-2_system"]
    
        
    orange_coupled_trainset = OrangeCoupledDataSet(coupled_trainset, "rank", [], meta_attributes, "trainset.tab")
    
    print "coupling test set"
    coupled_testset = CoupledDataSet(simple_testset)
    simple_testset = None
    print "orange version of coupling test set"
    orange_coupled_testset = OrangeCoupledDataSet(coupled_testset, "rank", [], meta_attributes, "testset.tab")
    
    bayes_learner = BayesLearner()
    bayes_classifier = OrangeClassifier(bayes_learner(orange_coupled_trainset.get_data()))
    print bayes_classifier.classify_orange_table(orange_coupled_testset.get_data())
        
    
#    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    