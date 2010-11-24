#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
@author: Eleftherios Avramidis
"""

from io.input.xmlreader import XmlReader
from io.input.orangereader import OrangeData
from classifier.bayes import Bayes
from classifier.tree import TreeLearner
from classifier.svm import SVM


if __name__ == '__main__':
    
    filename = "/home/elav01/workspace/TaraXUscripts/data/evaluations_feat.jcml"
    class_name = "rank"
    desired_attributes = []
    
    #Load data from external file
    pdr = XmlReader(filename) 
    dataset =  pdr.get_dataset()
    
    
    desired_attributes=['langsrc', 'langtgt', 'testset']
    
    #convert data in orange format
    orangedata = OrangeData( dataset, class_name, desired_attributes )
    
    orig_dataset = orangedata.get_dataset()
    
    i=0
    for ps1 in orig_dataset.get_parallelsentences()[0:10]:
        ps2 = dataset.get_parallelsentences()[i]
        print ps1.get_source().get_string() , "\n",  ps2.get_source().get_string()
        print ps1.get_attributes() , "\n", ps2.get_attributes()
        print ps1.get_translations()[0].get_string() , "\n",  ps2.get_translations()[0].get_string()
        print ps1.get_translations()[0].get_attributes() , "\n",  ps2.get_translations()[0].get_attributes()
        print ps1.get_translations()[1].get_string() , "\n",  ps2.get_translations()[1].get_string()
        print ps1.get_translations()[1].get_attributes() , "\n",  ps2.get_translations()[1].get_attributes()
    
    
    #split data the orange way (stratified)
    [training_part, test_part] = orangedata.split_data(0.1)
    training_data = OrangeData(training_part, class_name)
    test_data = OrangeData(test_part, class_name)
    
    print "DATASET------"
    orig_test_data = test_data.get_dataset()
    
    
    
    orangedata.cross_validation()
    orangedata.print_statistics()
    
    #train data
    bayes = Bayes( training_data )
    tree = TreeLearner( training_data )
    svm = SVM ( training_data )
    
    bayes.name = "bayes"
    tree.name = "tree"
    svm.name = "SVM"
    classifiers = [bayes, tree, svm]
    
    # compute accuracies
    acc = test_data.get_accuracy(classifiers)
    print "Classification accuracies:"
    for i in range(len(classifiers)):
        print classifiers[i].name, "\t", acc[i]
        
        
    