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
import pickle
import orange, orngLR
from sentence.dataset import DataSet

from io.input.orangereader import OrangeData
from io.output.xmlwriter import XmlWriter
 
class Experiment:

    desired_attributes={ 
                            'tgt-1_prob' :'c',
                            'tgt-2_prob' :'c',
                            'src_berkeley-n' : 'c',
                            'tgt-1_berkeley-n' : 'c',
                            'tgt-2_berkeley-n' : 'c',
                            'src_berkeley-best-parse-confidence' : 'c',
                            'tgt-1_berkeley-best-parse-confidence' : 'c', 
                            'tgt-2_berkeley-best-parse-confidence' : 'c',
                            'src_berkeley-avg-confidence' :'c',
                            'tgt-1_berkeley-avg-confidence' :'c', 
                            'tgt-2_berkeley-avg-confidence' :'c',
                            'src_length_ratio' :'d',
                            'tgt-1_length_ratio' :'d',
                            'tgt-2_length_ratio' :'d',
                            'src_length' :'d',
                            'tgt-1_length' :'d',
                            'tgt-2_length' :'d',
                            
                            }
    
    def split_corpus(self, filename, filename_train, filename_test, proportion=0.1):
        #filename = os.getenv("HOME") + "/taraxu_data/wmt08-humaneval-data/wmt08_human_binary.jcml"
        class_name = "rank"
        
        #self.desired_attributes = []
        
        #Load data from external file
        pdr = XmlReader(filename) 
        dataset =  pdr.get_dataset()
        
        
        self.desired_attributes = {'tgt-1_system' : 'd', 
                                   'tgt-2_system' : 'd',
                                   'tgt-3_system' : 'd',
                                   'tgt-4_system' : 'd',
                                   'tgt-5_system' : 'd',
                                   'segment_id' : 'd', 
                                   'id' : 'd',
                                   'document_id' : 'd',
                                   'judge_id': 'd'}
        
        
        #convert data in orange format
        orangedata = OrangeData( dataset, class_name, self.desired_attributes )
        
        #orig_dataset = orangedata.get_dataset()
        
        i=0
        
        #split data the orange way (stratified)
        [training_part, test_part] = orangedata.split_data(proportion)
        training_data = OrangeData(training_part, class_name)
        test_data = OrangeData(test_part, class_name)
        
        print "TESTSET------"
        orig_test_data = test_data.get_dataset()    
        xmlwriter = XmlWriter(orig_test_data)
        xmlwriter.write_to_file(filename_test)
        orig_test_data = None
    
        print "TRAINSET------"
        orig_train_data = training_data.get_dataset()    
        xmlwriter = XmlWriter(dataset)
        xmlwriter.write_to_file(filename_train)
    
    """
    Splits a judgments set into two sets, one testset and one training set. Allows for extra criteria 
    for the test set, such as no-repetitive judgments and clear ranking (no ties)
    @param  filename: pointing to the xml file containing the original full set to be read from
    @param filename_train: xml file to be created with the training data
    @param filename_test: xml file to be created with the test data
    @param ties_threshold: test sentences will be dropped, if they have nore than n ties when ranked
    """
    def get_test_sentences(self, filename, filename_train, filename_test, ties_threshold = 1, max_sentences = 100):
        reader = XmlReader(filename)
        parallelsentences = reader.get_parallelsentences()
        
        prev_id = None
        repeats = 1
        single_ids = []
        prev_ps = None
        
        #get unique judgments
        for parallelsentence in parallelsentences:
            if prev_id == parallelsentence.get_attribute("id"):
                repeats += 1
            elif prev_ps:
                repeats = 1
                #choose the sentence as test sentence, only if it appears once and 
                #doesn't have to many ranking ties
                if repeats == 1 and self.count_ties(prev_ps) < ties_threshold:
                    single_ids.append(prev_id)
                
            prev_id = parallelsentence.get_attribute("id")
            prev_ps = parallelsentence
       
        os.sys.stderr.write("%d sentences chosen\n" % len(single_ids))
        
        single_ids = single_ids[0:max_sentences-1]
        testset = []
        trainset = []
        
        for parallelsentence in parallelsentences:
            if parallelsentence.get_attribute("id") in single_ids:
                testset.append(parallelsentence)
            else:
                trainset.append(parallelsentence)
        
        
        tmp_dataset = DataSet(trainset)
        xmlwriter = XmlWriter(tmp_dataset)
        xmlwriter.write_to_file(filename_train)
        
        tmp_dataset = DataSet(testset)
        xmlwriter = XmlWriter(tmp_dataset)
        xmlwriter.write_to_file(filename_test)
            
        
    def count_ties(self, parallelsentence):
        ranks = []
        ties = 0
        for translation in parallelsentence.get_translations():
            ranks.append (translation.get_attribute("rank"))
            
        for rank_value in set(ranks):
            ranks_count = ranks.count(rank_value)
            if (ranks_count > 1):
                ties += ranks_count-1
        return ties
                
    
    def add_external_features(self, given_filename="evaluations_all.jcml"):
        
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
        srilm_en = SRILMFeatureGenerator("http://134.96.187.4:8585", "en" )
        #srilm_de = SRILMFeatureGenerator("http://134.96.187.4:8586", "de" )
        
        #Berkeley feature generator
        berkeley_en = BerkeleyFeatureGenerator("http://localhost:8682", "en")
        berkeley_de = BerkeleyFeatureGenerator("http://localhost:8683", "de")
        
        
        #proceed with parcing
        saxreader = SaxJCMLProcessor( file_object2, [lfg, srilm_en, berkeley_en, berkeley_de] )
        myparser = make_parser( )
        myparser.setContentHandler( saxreader )
        myparser.parse( file_object )
       
    
    def train_classifiers(self, filename="evaluations_all.jcml"):
        if filename.endswith(".tab"):
            orangetable = orange.ExampleTable(filename)
            print "Passing data to Orange"
            training_data = OrangeData(orangetable)
        else:
            print "Reading XML"
            reader = XmlReader(filename)
            dataset =  reader.get_dataset()
            class_name = "rank"
            #TODO: get list of attributes directly from feature generators
           
            print "Passing data to Orange"
            training_data = OrangeData(dataset, class_name, self.desired_attributes, True)
            dataset=None
            #train data
            #training_data.cross_validation()
        #training_data.print_statistics()
        # compute accuracies
        
        print "training loglinear"
#        lr = orngLR.LogRegLearner(training_data.get_data()) # compute classification accuracy
        print "Bayes" 
        bayes = Bayes( training_data )
        print "Tree"
        tree = TreeLearner( training_data )
        print "SVM"
        svm = SVM ( training_data )
        
    
        bayes.name = "bayes"
        tree.name = "tree"
        svm.name = "SVM"
        #lr.name = "logl"
        
        
        return [ bayes, tree, svm]
        
    
    def test_classifiers(self, classifiers, filename):
        reader = XmlReader(filename)
        dataset =  reader.get_dataset()
        
        
        class_name = "rank"
        test_data = OrangeData(dataset, class_name, self.desired_attributes)
        acc = test_data.get_accuracy(classifiers)
        print "Classification accuracies:"
        for i in range(len(classifiers)):
            print classifiers[i].name, "\t", acc[i]
            
        
    def test_length_fg_with_full_parsing(self):
        dir = getenv("HOME") + "/workspace/TaraXUscripts/data"
        filename = dir + "/evaluations_feat.jcml"
        class_name = "rank"
        self.desired_attributes = []
        
        #Load data from external file
        pdr = XmlReader(filename) 
        dataset =  pdr.get_dataset()
        
        
        self.desired_attributes=['langsrc', 'langtgt', 'testset']
        
        
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
    #add_external_features("train08.xml")
    
    #myexperiment = Experiment()

    exp = Experiment()
    exp.get_test_sentences("/home/elav01/taraxu_data/wmt10-humaneval-data/wmt10.jcml", "/home/elav01/taraxu_data/wmt10-humaneval-data/wmt10-train.jcml" , "/home/elav01/taraxu_data/wmt10-humaneval-data/wmt10-test.jcml")
    
    #myexperiment.add_external_features("test08.xml")
    
#    train_filename = dir + "featured_train08.xml"
#    classifiers = myexperiment.train_classifiers('/home/elav01/workspace/TaraXUscripts/src/tmpa04du_.tab')
#    #classifiers = myexperiment.train_classifiers('/home/elav01/workspace/TaraXUscripts/src/tmpa04du_.tab')
#    test_filename = dir + "featured_test08.xml"
#    myexperiment.test_classifiers(classifiers, test_filename)
    
        
    