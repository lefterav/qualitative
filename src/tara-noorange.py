#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
@author: Eleftherios Avramidis
"""

from io.input.xmlreader import XmlReader
#from io.input.orangereader import OrangeData
from io.output.xmlwriter import XmlWriter
from classifier.bayes import Bayes
from classifier.tree import TreeLearner
from classifier.svm import SVM
from os import getenv

if __name__ == '__main__':
    
    dir = getenv("HOME") + "/workspace/TaraXUscripts/data"
    filename = dir + "/evaluations_feat.jcml"
    class_name = "rank"
    desired_attributes = []
    
    #Load data from external file
    pdr = XmlReader(filename) 
    dataset =  pdr.get_dataset()
    
    
    desired_attributes=['langsrc', 'langtgt', 'testset']
    
    
    #xmlwriter = XmlWriter(dataset)
    #xmlwriter.write_to_file(dir + "/test.xml")
    
    from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
    
    fg = LengthFeatureGenerator()
    
    fdataset = fg.add_features( dataset )
    dataset = None
    
 
    
    xmlwriter = XmlWriter(fdataset)
    xmlwriter.write_to_file(dir + "/test-length.xml")
    
    
        
    