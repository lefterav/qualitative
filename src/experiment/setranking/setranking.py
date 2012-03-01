'''
Created on 23 Feb 2012

@author: lefterav
'''

from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet
from io.sax.saxps2jcml import Parallelsentence2Jcml
from orange import BayesLearner 
from classifier.classifier import OrangeClassifier
from orange import ExampleTable


if __name__ == '__main__':
    
    #param
    input_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.jcml" 
    #param
    output_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.coupled.jcml"
    
    print "loading big set"
    simple_dataset = JcmlReader(input_file).get_dataset() 
    
    print "concatenating set for development purposes"
    simple_dataset, a = simple_dataset.split(0.01)
    
    print "writing down the concatenated set"
    Parallelsentence2Jcml(simple_dataset.get_parallelsentences()).write_to_file('/home/elav01/taraxu_data/wmt12/qe/training_set/training-sample.jcml')
    
    print "arbitrarily split given set to training and test sets 90% + 10%"
    simple_trainset, simple_testset = simple_dataset.split(0.9)
    simple_dataset = None
    
    print "TRAINING"
    print "coupling training set"
    coupled_trainset = CoupledDataSet(simple_trainset)
    simple_trainset = None
    
    print "orange version of coupling training set"
    #param
    meta_attributes = ["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", "ps1_id", "ps2_id", "tgt-1_score" , "tgt-2_score", "tgt-1_system" , "tgt-2_system"]
    orange_coupled_trainset = OrangeCoupledDataSet(coupled_trainset, "rank", [], meta_attributes, "trainset.tab", True)
    
    #param
    bayes_learner = BayesLearner()
    bayes_classifier = OrangeClassifier(bayes_learner(ExampleTable("trainset.tab")))
    
    print "TESTING"
    print "coupling test set"
    coupled_testset = CoupledDataSet(simple_testset)
    simple_testset = None
    print "orange version of coupling test set"
    orange_coupled_testset = OrangeCoupledDataSet(coupled_testset, "rank", [], meta_attributes, "testset.tab", True)
    classified_set_vector = bayes_classifier.classify_orange_table(ExampleTable("testset.tab"))
    
    print "EVALUATION"
    att_vector = dict([("rank_predicted", v[0]) for v in classified_set_vector])
    coupled_testset.add_attribute_vector(att_vector, "ps")
    Parallelsentence2Jcml("reconstructed_testset").write_to_file("testset_predicted.jcml")
    
    
    
    reconstructed_testset = coupled_testset.get_single_set()
    Parallelsentence2Jcml("reconstructed_testset").write_to_file("reconstructed.jcml")
    
    
#    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    