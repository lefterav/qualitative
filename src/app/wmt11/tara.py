#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
@author: Eleftherios Avramidis
"""

from io_utils.input.xmlreader import XmlReader
from io_utils.input.orangereader import OrangeData
from io_utils.output.xmlwriter import XmlWriter
from classifier.bayes import Bayes
from classifier.tree import TreeLearner
from classifier.svm import SVM
import os


if __name__ == '__main__':
    
    filename = os.getenv("HOME") + "/workspace/TaraXUscripts/data/wmt08_human_binary.jcml"
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
    
    
    #split data the orange way (stratified)
    [training_part, test_part] = orangedata.split_data(0.1)
    training_data = OrangeData(training_part, class_name)
    test_data = OrangeData(test_part, class_name)
    
    print "DATASET------"
    orig_test_data = test_data.get_dataset()
    
    xmlwriter = XmlWriter(dataset)
    xmlwriter.write_to_file(os.getenv("HOME") + "/workspace/TaraXUscripts/data/test.xml")
    
    from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
    fg = LengthFeatureGenerator()
    fdataset = fg.add_features( orig_dataset )
    xmlwriter = XmlWriter(fdataset)
    xmlwriter.write_to_file(os.getenv("HOME") + "/workspace/TaraXUscripts/data/test-length.xml")
    
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
        
        
    