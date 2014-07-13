'''
Created on 23 Feb 2012

@author: Eleftherios Avramidis
'''

from io_utils.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.sax.saxjcml2orange import SaxJcml2Orange
from Orange.classification.bayes import NaiveLearner as BayesLearner 
from classifier.classifier import OrangeClassifier
from Orange.data import Table as ExampleTable
from Orange.core import DomainContinuizer 
from classifier.svmeasy import SVMEasyLearner as SVMEasy
import Orange
import sys
import cPickle as pickle
import os

if __name__ == '__main__':
    
    #param
    path = sys.argv[1]
    step = int(sys.argv[2])
    input_file = sys.argv[3] #"/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training-sample.jcml"
    if len(sys.argv) > 4:
        test_file = sys.argv[4]
    else:
        test_file = None
    
    os.chdir(path) 
    #param
#    output_file = "/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training.coupled.jcml"
    if step < 1:
        print "loading big set"
        simple_trainset = JcmlReader(input_file).get_dataset() 
    
#        print "concatenating set for development purposes"
#        simple_trainset, a = simple_trainset.split(0.07)
#    
#    print "writing down the concatenated set"
#    Parallelsentence2Jcml(simple_dataset.get_parallelsentences()).write_to_file('/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training-sample.jcml')
#    
        if not test_file:
            print "arbitrarily split given set to training and test sets 90% + 10%"
            simple_trainset, simple_testset = simple_trainset.split(0.9)
            Parallelsentence2Jcml(simple_trainset).write_to_file("trainset.jcml")
            Parallelsentence2Jcml(simple_testset).write_to_file("testset.jcml")
        else:
            simple_testset = JcmlReader(test_file).get_dataset() 
            
    if step<2:
        print "TRAINING"
        print "coupling training set"
        CoupledDataSetDisk(simple_trainset).write("trainset.coupled.jcml", "score", 2.0, True)
    #    coupled_trainset = CoupledDataSet(readfile = "trainset.coupled.jcml")
        simple_trainset = None
    
    if step<3:
        print "orange version of coupling training set"
        #param
        meta_attributes = set(["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", 
                               "ps1_id", "ps2_id", "tgt-1_score" , "tgt-2_score", "tgt-1_system" , "tgt-2_system", "tgt-2_berkeley-tree", "tgt-1_berkeley-tree", "src-1_berkeley-tree", "src-2_berkeley-tree", 
                                 ])
        
        discrete_attributes = [ "src-1_reuse_status", "src-2_reuse_status", 
                               "src-1_terminologyAdmitted_status", 
                               "src-2_terminologyAdmitted_status", 
                               "src-2_total_status", "src-1_total_status", 
                               "src-1_spelling_status", "src-2_spelling_status", 
                               "src-1_style_status", "src-2_style_status", 
                               "src-1_grammar_status", "src-2_grammar_status", 
                               "src-2_terminology_status", "src-1_terminology_status",
                               "src-1_resultStats_projectStatus", "src-2_resultStats_projectStatus"
                               ]
        
        
    #    active_attributes = list(set(coupled_trainset.get_all_attribute_names()) - meta_attributes)
        active_attributes = []
        
        
        
        
        orange_coupled_trainset = SaxJcml2Orange("trainset.coupled.jcml", 
                                                 "rank", 
                                                 active_attributes, 
                                                 meta_attributes, 
                                                 "/tmp/trainset.coupled.disk.tab", 
                                                 compact_mode = True, 
                                                 discrete_attributes=discrete_attributes, 
                                                 get_nested_attributes=False,
                                                 )

        
#    coupled_trainset = CoupledDataSet(readfile="trainset.coupled.jcml")
#    orange_coupled_trainset = OrangeCoupledDataSet(coupled_trainset, "rank", active_attributes , meta_attributes, "trainset.coupled.memory.tab", True)
#    
    
    if step<4:
        #param
#        mylearner = SVMEasy()
#        
#        params = dict(continuize=True, \
#            multinomialTreatment=DomainContinuizer.NValues, \
#            continuousTreatment=DomainContinuizer.NormalizeBySpan, \
#            classTreatment=DomainContinuizer.Ignore)
        mylearner = BayesLearner()
    

        myclassifier = OrangeClassifier(mylearner(ExampleTable("trainset.coupled.disk.tab")))
        
        objectfile = open("classifier.pickle", 'w')
        pickle.dump(myclassifier.classifier, objectfile)
        objectfile.close()
    
    if step<5:    
        print "TESTING"
        print "coupling test set"
        CoupledDataSetDisk(simple_testset).write("testset.coupled.jcml")
    
    
    if step<7:
        simple_testset = None
        print "orange version of coupling test set"
        orange_coupled_trainset = SaxJcml2Orange("testset.coupled.jcml", "rank", 
                                                 active_attributes, 
                                                 meta_attributes, 
                                                 "testset.coupled.tab", 
                                                 compact_mode=True, 
                                                 discrete_attributes=discrete_attributes, 
                                                 get_nested_attributes=False)    
    #    orange_coupled_testset = OrangeCoupledDataSet(coupled_testset, "rank", [], meta_attributes, "testset.tab", True)
    if step<8:
        print "performing classification"
        classified_set_vector = myclassifier.classify_orange_table(ExampleTable("testset.coupled.tab"))
        print classified_set_vector
        
    if step<9:
        print "EVALUATION"
        print "reloading coupled test set"
        coupled_testset = CoupledDataSet(readfile = "testset.coupled.jcml")
        
        print "adding attribute vector"
        att_vector = [{"rank_predicted": v[0]} for v in classified_set_vector]
        print att_vector
        coupled_testset.add_attribute_vector(att_vector, "ps")
        Parallelsentence2Jcml(coupled_testset).write_to_file("testset.classified.jcml")
#    Parallelsentence2Jcml(reconstructed_testset).write_to_file("testset_predicted.jcml")
    
    
    
        reconstructed_testset = coupled_testset.get_single_set()
#    Parallelsentence2Jcml("reconstructed_testset").write_to_file("reconstructed.jcml")
    
    
#    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    