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
import os

from io.input.orangereader import OrangeData
from io.output.xmlwriter import XmlWriter

def split_corpus():
    filename = os.getenv("HOME") + "/taraxu_data/wmt08-humaneval-data/wmt08_human_binary.jcml"
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
    
    print "TESTSET------"
    orig_test_data = test_data.get_dataset()    
    xmlwriter = XmlWriter(orig_test_data)
    xmlwriter.write_to_file(os.getenv("HOME") + "/workspace/TaraXUscripts/data/test08.xml")
    orig_test_data = None

    print "TRAINSET------"
    orig_train_data = training_data.get_dataset()    
    xmlwriter = XmlWriter(dataset)
    xmlwriter.write_to_file(os.getenv("HOME") + "/workspace/TaraXUscripts/data/train08.xml")

    


def add_external_features(given_filename="evaluations_all.jcml"):
    
    from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
    from featuregenerator.lm.srilm.srilmclient import SRILMFeatureGenerator
    from featuregenerator.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator 
    from io.saxjcml import SaxJCMLProcessor
    from xml.sax import make_parser
    import codecs
    
    dir = getenv("HOME") + "/workspace/TaraXUscripts/data"
    filename = dir + "/" + given_filename
    file_object = codecs.open(filename, 'r', 'utf-8')
    

    dir = getenv("HOME") + "/workspace/TaraXUscripts/data"
    filename_out = dir + "/featured_" + given_filename
    file_object2 = codecs.open(filename_out, 'w', 'utf-8')

    ###INITIALIZE FEATURE GENERATORS

    lfg = LengthFeatureGenerator()
    
    #SRILM feature generator
    #srilm_en = SRILMFeatureGenerator("http://134.96.187.4:8585", "en" )
    srilm_de = SRILMFeatureGenerator("http://134.96.187.4:8586", "de" )
    
    #Berkeley feature generator
    berkeley_en = BerkeleyFeatureGenerator("http://localhost:8682", "en")
    berkeley_de = BerkeleyFeatureGenerator("http://localhost:8683", "de")
    
    
    #proceed with parcing
    saxreader = SaxJCMLProcessor( file_object2, [lfg, srilm_de, berkeley_en, berkeley_de] )
    myparser = make_parser( )
    myparser.setContentHandler( saxreader )
    myparser.parse( file_object )
    
   

def train_classifiers(filename="evaluations_all.jcml"):
    reader = XmlReader(filename)
    dataset =  reader.get_dataset()
    class_name = "rank"
    #TODO: get list of attributes directly from feature generators
    desired_attributes={'tgt-1_berkeley-n' : 'c', 
                        'tgt-1_berkeley-best-parse-confidence' : 'c', 
                        'tgt-1_berkeley-avg-confidence' :'c',
                        'tgt-1_prob' :'c',
                        'tgt-1_system' :'d',
                        'tgt-1_length_ratio' :'d',
                        'tgt-2_berkeley-n' : 'c',
                        'tgt-2_berkeley-best-parse-confidence' : 'c', 
                        'tgt-2_berkeley-avg-confidence' :'c',
                        'tgt-2_prob' :'c',
                        'tgt-2_system' :'d',
                        'tgt-2_length_ratio' :'d',
                        }
    
    training_data = OrangeData(dataset, class_name, desired_attributes)
    
    #train data
    bayes = Bayes( training_data )
    tree = TreeLearner( training_data )
    svm = SVM ( training_data )
    
    bayes.name = "bayes"
    tree.name = "tree"
    svm.name = "SVM"
    classifiers = [bayes, tree, svm]
    
    training_data.cross_validation()
    training_data.print_statistics()
    # compute accuracies
    
    import orange, orngLR
    
    lr = orngLR.LogRegLearner(training_data.get_data()) # compute classification accuracy 
    correct = 0.0 
    for ex in training_data.get_data: 
        if lr(ex) == ex.getclass(): 
            correct += 1
    print "Classification accuracy:", correct/len(training_data.get_data()) 
    orngLR.printOUT(lr) 
    
    
    
    
    
def test_length_fg_with_full_parsing():
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
    

if __name__ == '__main__':
    dir = getenv("HOME") + "/workspace/TaraXUscripts/data/"
    
    #add_external_features()
    #split_corpus()
    add_external_features("train08.xml")
    
    #filename = dir + "featured_test08.xml"
    #train_classifiers(filename)
    
        
    