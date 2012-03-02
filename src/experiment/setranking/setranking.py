'''
Created on 23 Feb 2012

@author: lefterav
'''

from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from io.sax.saxps2jcml import Parallelsentence2Jcml
from orange import BayesLearner 
from classifier.classifier import OrangeClassifier
from orange import ExampleTable
from classifier.svmeasy import SVMEasy
import orange
import sys
import cPickle as pickle
import os

if __name__ == '__main__':
    
    #param
    path = sys.argv[1]
    input_file = sys.argv[2] #"/home/elav01/taraxu_data/wmt12/qe/training_set/training-sample.jcml"
    if len(sys.argv) > 3:
        test_file = sys.argv[3]
    else:
        test_file = None
    
    os.chdir(path) 
    #param
#    output_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.coupled.jcml"
    
    print "loading big set"
    simple_trainset = JcmlReader(input_file).get_dataset() 
    
#    print "concatenating set for development purposes"
#    simple_dataset, a = simple_dataset.split(0.01)
#    
#    print "writing down the concatenated set"
#    Parallelsentence2Jcml(simple_dataset.get_parallelsentences()).write_to_file('/home/elav01/taraxu_data/wmt12/qe/training_set/training-sample.jcml')
#    
    if not test_file:
        print "arbitrarily split given set to training and test sets 90% + 10%"
        simple_trainset, simple_testset = simple_trainset.split(0.9)
        Parallelsentence2Jcml(simple_trainset).write_to_file("trainset.jcml")
        Parallelsentence2Jcml(simple_testset).write_to_file("testset.jcml")
    else:
        simple_testset = JcmlReader(test_file).get_dataset() 
        
    
    print "TRAINING"
    print "coupling training set"
    CoupledDataSetDisk(simple_trainset).write("trainset.coupled.jcml")
    coupled_trainset = CoupledDataSet(readfile = "trainset.coupled.jcml")
    simple_trainset = None
    
    print "orange version of coupling training set"
    #param
    meta_attributes = set(["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", "ps1_id", "ps2_id", "tgt-1_score" , "tgt-2_score", "tgt-1_system" , "tgt-2_system"])
    active_attributes = list(set(coupled_trainset.get_all_attribute_names()) - meta_attributes)
    
    orange_coupled_trainset = OrangeCoupledDataSet(coupled_trainset, "rank", active_attributes , meta_attributes, "trainset.tab", True)
    
    #param
    mylearner = SVMEasy()
    
    params = dict(continuize=True, \
        multinomialTreatment=orange.DomainContinuizer.NValues, \
        continuousTreatment=orange.DomainContinuizer.NormalizeBySpan, \
        classTreatment=orange.DomainContinuizer.Ignore)
    myclassifier = OrangeClassifier(mylearner.learnClassifier(ExampleTable("trainset.tab"), params))
    
    objectfile = open("classifier.pickle", 'w')
    pickle.dump(myclassifier.classifier, objectfile)
    objectfile.close()
    
    print "TESTING"
    print "coupling test set"
    CoupledDataSetDisk(simple_testset).write("testset.coupled.jcml")
    coupled_testset = CoupledDataSet(readfile = "testset.coupled.jcml")

    simple_testset = None
    print "orange version of coupling test set"
    orange_coupled_testset = OrangeCoupledDataSet(coupled_testset, "rank", [], meta_attributes, "testset.tab", True)
    classified_set_vector = myclassifier.classify_orange_table(ExampleTable("testset.tab"))
    print classified_set_vector
    
    print "EVALUATION"
    att_vector = [{"rank_predicted": v[0]} for v in classified_set_vector]
    print att_vector
    coupled_testset.add_attribute_vector(att_vector, "ps")
    Parallelsentence2Jcml(coupled_testset).write_to_file("testset.classified.jcml")
#    Parallelsentence2Jcml(reconstructed_testset).write_to_file("testset_predicted.jcml")
    
    
    
    reconstructed_testset = coupled_testset.get_single_set()
#    Parallelsentence2Jcml("reconstructed_testset").write_to_file("reconstructed.jcml")
    
    
#    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    