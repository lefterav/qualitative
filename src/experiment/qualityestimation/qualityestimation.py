'''
Created on 23 Feb 2012

@author: lefterav
'''

from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet, OrangeCoupledDataSet, CoupledDataSetDisk
from io.sax.saxps2jcml import Parallelsentence2Jcml
from io.sax.saxjcml2orange import SaxJcml2Orange
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
    step = int(sys.argv[2])
    input_file = sys.argv[3] #"/home/elav01/taraxu_data/wmt12/qe/training_set/training-sample.jcml"
    if len(sys.argv) > 4:
        test_file = sys.argv[4]
    else:
        test_file = None
    
    os.chdir(path) 
    #param
#    output_file = "/home/elav01/taraxu_data/wmt12/qe/training_set/training.coupled.jcml"
    if step < 1:
        print "loading big set"
        simple_trainset = JcmlReader(input_file).get_dataset() 
    
        print "concatenating set for development purposes"
        simple_trainset, a = simple_trainset.split(0.07)
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
            

    
    if step<3:
        print "orange version of coupling training set"
        #param
        meta_attributes = set(["testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", 
                               "id", "tgt-1_score" ,  "tgt-1_system" ,  "tgt-1_berkeley-tree", "src_berkeley-tree",  
                                 ])
        
        discrete_attributes = [ "src_reuse_status",  
                               "src_terminologyAdmitted_status", 
                               "src_total_status", 
                               "src_spelling_status",  
                               "src_style_status",  
                               "src_grammar_status",  
                               "src_terminology_status",
                               "src_resultStats_projectStatus", 
                               ]
        
        
    #    active_attributes = list(set(coupled_trainset.get_all_attribute_names()) - meta_attributes)
        active_attributes = []
        orange_coupled_trainset = SaxJcml2Orange("trainset.jcml", 
                                                 "tgt-1_score", 
                                                 active_attributes, 
                                                 meta_attributes, 
                                                 "trainset.disk.tab", 
                                                 compact_mode = True, 
                                                 discrete_attributes=discrete_attributes, 
                                                 get_nested_attributes=True,
#                                                 filter_attributes={"rank" : "0"},
                                                 class_type="d"
                                                 )
        
#    coupled_trainset = CoupledDataSet(readfile="trainset.coupled.jcml")
#    orange_coupled_trainset = OrangeCoupledDataSet(coupled_trainset, "rank", active_attributes , meta_attributes, "trainset.coupled.memory.tab", True)
#    
    
    if step<4:
        #param
        mylearner = orange.LinearLearner()
        myclassifier = mylearner(ExampleTable("trainset.disk.tab"))

        
#        params = dict(continuize=True, \
#            multinomialTreatment=orange.DomainContinuizer.NValues, \
#            continuousTreatment=orange.DomainContinuizer.NormalizeBySpan, \
#            classTreatment=orange.DomainContinuizer.Ignore)
        myclassifier = OrangeClassifier(mylearner(ExampleTable("trainset.disk.tab")), {})
        
        objectfile = open("classifier.pickle", 'w')
        pickle.dump(myclassifier.classifier, objectfile)
        objectfile.close()
    

    
    
    if step<7:
        
        meta_attributes.add("tgt-1_score")
        print "orange version of coupling test set"
        orange_coupled_testset = SaxJcml2Orange("testset.jcml", "tgt-1_score", 
                                                 active_attributes, 
                                                 meta_attributes, 
                                                 "testset.tab", 
                                                 compact_mode=True, 
                                                 discrete_attributes=discrete_attributes, 
                                                 get_nested_attributes=True)    
    #    orange_coupled_testset = OrangeCoupledDataSet(coupled_testset, "rank", [], meta_attributes, "testset.tab", True)
    if step<8:
        print "performing classification"
        classified_set_vector = myclassifier.classify_orange_table(ExampleTable("testset.tab"))
        print classified_set_vector
        
    if step<9:
        print "EVALUATION"
        print "reloading coupled test set"
        
        
        print "adding attribute vector"
        att_vector = [{"rank_predicted": v[0]} for v in classified_set_vector]
        print att_vector
        simple_testset.add_attribute_vector(att_vector, "ps")
        Parallelsentence2Jcml(simple_testset).write_to_file("testset.classified.jcml")
#    Parallelsentence2Jcml(reconstructed_testset).write_to_file("testset_predicted.jcml")
    
    
    
#        reconstructed_testset = simple_testset.get_single_set()
#    Parallelsentence2Jcml("reconstructed_testset").write_to_file("reconstructed.jcml")
    
    
#    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    