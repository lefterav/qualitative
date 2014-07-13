#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
@author: Eleftherios Avramidis
"""

from io_utils.input.xmlreader import XmlReader
from io_utils.input.taraxureader import TaraXUReader
#from io_utils.input.orangereader import OrangeData
from io_utils.output.xmlwriter import XmlWriter

from os import getenv
import os
import pickle

from sentence.dataset import DataSet




from io_utils.saxjcml import SaxJCMLProcessor
from xml.sax import make_parser
from sentence.rankhandler import RankHandler
import sys

 
class Experiment:
    desired_attributes = []
    meta_attributes = [ "id" , 
                       "testset" , 
                       "judge_id", 
                       "segment_id", 
                       "tgt-1_berkeley-tree", 
                       "tgt-2_berkeley-tree", 
                       "src_berkeley-tree", 
                       "langsrc", 
                       "langtgt", 
                       'tgt-1_system', 
                       'tgt-2_system', 
                       'document_id']
    
    def __init__(self):
        pass 
        #length radio, unk, loglikelihood_ratio, berkeley-n_ratio', VP_ratio'
        self.desired_attributes = [
                                   "tgt-1_unk",
                                   "tgt-2_unk",
                                   "tgt-1_length_ratio",
                                   "tgt-2_length_ratio",
                                   "tgt-1_berkeley-n_ratio" ,
                                   "tgt-2_berkeley-n_ratio" ,
                                   "tgt-1_parse-VP_ratio" ,
                                   "tgt-2_parse-VP_ratio" ,
                                   #"tri-prob_diff",
                                   "tgt-1_berkley-loglikelihood_ratio",
                                   "tgt-2_berkley-loglikelihood_ratio"
                                   #"berkeley-avg-confidence_ratio_diff"
                                   ]
#        desired_att_list = [
#                            #===================================================
        self.desired_attributes = ['tgt-1_berkeley-avg-confidence_ratio',
                             'tgt-1_length_ratio', 
                             'tgt-1_berkeley-avg-confidence', 
                             'tgt-2_berkeley-avg-confidence_ratio', 
                             'tgt-2_berkeley-best-parse-confidence_ratio', 
                             'tgt-2_parse-dot', 
                             'tgt-2_parse-VP', 
                             'tgt-2_length_ratio', 
                             'tgt-2_parse-comma', 
                             'tgt-1_parse-dot', 
                             'tgt-2_berkley-loglikelihood_ratio', 
                             'tgt-2_uni-prob', 'tgt-2_parse-VB', 
                             'tgt-1_parse-NN_ratio', 
                             'src_parse-dot', 
                             'tgt-1_length', 
                             'tgt-2_prob', 
                             'src_parse-comma', 
                             'src_parse-NP', 
                             'tgt-2_parse-VP_ratio', 
                             'tgt-1_parse-comma_ratio', 
                             'src_parse-NN', 
                             'tgt-1_berkeley-n_ratio', 
                             'tgt-2_parse-PP', 
                             'tgt-1_parse-PP_ratio', 
                             'tgt-2_parse-comma_ratio', 
                             'tgt-1_unk', 
                             'tgt-1_parse-NP', 
                             'tgt-1_berkeley-best-parse-confidence_ratio', 
                             'tgt-2_parse-NP_ratio', 
                             'tgt-1_berkeley-n', 
                             'tgt-1_tri-prob', 
                             'tgt-1_parse-NP_ratio', 
                             'src_length', 
                             'tgt-2_unk', 
                             'tgt-1_berkley-loglikelihood', 
                             'src_berkeley-best-parse-confidence', 
                             'tgt-2_berkley-loglikelihood', 
                             'src_berkley-loglikelihood',
                             'tgt-1_prob',
                             'tgt-2_parse-dot_ratio',
                             'tgt-2_berkeley-best-parse-confidence',
                             'src_parse-VVFIN',
                             'tgt-1_uni-prob',
                             'tgt-2_bi-prob',
                             'tgt-1_bi-prob',
                             'tgt-1_berkeley-best-parse-confidence',
                             'tgt-2_tri-prob',
                             'tgt-2_length',
                             'tgt-1_parse-NN',
                             'tgt-2_parse-NP',
                             'src_parse-VP',
                             'tgt-1_parse-PP',
                             'src_berkeley-n',
                             'tgt-1_parse-VP',
                             'tgt-2_parse-PP_ratio',
                             'tgt-1_berkley-loglikelihood_ratio',
                             'tgt-2_berkeley-n',
                             'tgt-2_berkeley-n_ratio',
                             'tgt-1_parse-VP_ratio',
                             'tgt-2_parse-NN_ratio',
                             'src_parse-PP',
                             'tgt-1_parse-dot_ratio',
                             'tgt-1_parse-VB',
                             'tgt-2_parse-NN',
                             'tgt-1_parse-comma',
                             'tgt-2_berkeley-avg-confidence',
                             'src_berkeley-avg-confidence' ]
                            #===================================================
                           
        
#        for desire_att in desired_att_list:
#            #if desire_att.endswith("prob"):
#            self.desired_attributes[desire_att] = 'c'

#    desired_attributes={ 
#                            'tgt-1_prob' :'c',
                           
#                            'tgt-2_prob' :'c',
#                            'src_berkeley-n' : 'c',
#                            'tgt-1_berkeley-n' : 'c',
#                            'tgt-2_berkeley-n' : 'c',
#                            'src_berkeley-best-parse-confidence' : 'c',
#                            'tgt-1_berkeley-best-parse-confidence' : 'c', 
#                            'tgt-2_berkeley-best-parse-confidence' : 'c',
#                            'src_berkeley-avg-confidence' :'c',
#                            'tgt-1_berkeley-avg-confidence' :'c', 
#                            'tgt-2_berkeley-avg-confidence' :'c',
#                            'src_length_ratio' :'d',
#                            'tgt-1_length_ratio' :'d',
#                            'tgt-2_length_ratio' :'d',
#                            'src_length' :'d',
#                            'tgt-1_length' :'d',
#                            'tgt-2_length' :'d',
#                            
#                            'src_parse-comma' : 'c',
#                            'tgt1_parse-comma' : 'c',
#                            'tgt2_parse-comma' : 'c',
#                            
#                            
#                        
#                            
#                            
#                            }
    
    def split_corpus(self, filename, filename_train, filename_test, proportion=0.1):
        
        from io_utils.input.orangereader import OrangeData
        
        #filename = os.getenv("HOME") + "/taraxu_data/wmt08-humaneval-data/wmt08_human_binary.jcml"
        class_name = "rank"
        
        #self.desired_attributes = []
        
        #Load data from external file
        pdr = XmlReader(filename) 
        dataset =  pdr.get_dataset()
        
        
#        self.desired_attributes = {'tgt-1_system' : 'd', 
#                                   'tgt-2_system' : 'd',
#                                   'tgt-3_system' : 'd',
#                                   'tgt-4_system' : 'd',
#                                   'tgt-5_system' : 'd',
#                                   'segment_id' : 'd', 
#                                   'id' : 'd',
#                                   'document_id' : 'd',
#                                   'judge_id': 'd'}
        
        
        #convert data in orange format
        orangedata = OrangeData( dataset, class_name, self.desired_attributes, self.meta_attributes )
        
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
    
   
    def get_test_sentences(self, filename, filename_train, filename_test, ties_threshold = 1, max_sentences = 100):
        """
        Splits a judgments set into two sets, one testset and one training set. Allows for extra criteria 
        for the test set, such as no-repetitive judgments and clear ranking (no ties)
        @param  filename: pointing to the xml file containing the original full set to be read from
        @param filename_train: xml file to be created with the training data
        @param filename_test: xml file to be created with the test data
        @param ties_threshold: test sentences will be dropped, if they have nore than n ties when ranked
        """
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
    
    
    
    
    def add_ngram_features_batch(self, filename, filename_out, server, language, format=None, lowercase=True, tokenize = True):
        if format == "taraxu":
            reader = TaraXUReader(filename)
        else:
            reader = XmlReader(filename)
        parallelsentences = reader.get_parallelsentences()
        reader = None
        from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
        srilm_ngram_en = SRILMngramGenerator(server, language, lowercase, tokenize)
        processed_parallelsentences = srilm_ngram_en.add_features_batch(parallelsentences)
        writer = XmlWriter(processed_parallelsentences)
        writer.write_to_file(filename_out)
        

    def add_b_features_batch(self, filename, filename_out, server, language, tokenize = False):
        reader = XmlReader(filename)
        parallelsentences = reader.get_parallelsentences()
        reader = None
        from featuregenerator.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator
        parser = BerkeleyFeatureGenerator(server, language, tokenize)
        parallesentences = parser.add_features_batch(parallelsentences);
        
        writer = XmlWriter(parallesentences)
        writer.write_to_file(filename_out)
    
    
    def add_external_features(self, filename, filename_out):
        from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
        from featuregenerator.lm.srilm.srilmclient import SRILMFeatureGenerator
        from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
        from featuregenerator.parser.berkeley.berkeleyclient import BerkeleyFeatureGenerator 
        
        #input_file_object = open(filename, 'r')
        input_file_object = open(filename, 'r' )
        output_input_file_object = open(filename_out, 'w' )
    
        ###INITIALIZE FEATURE GENERATORS
        lfg = LengthFeatureGenerator()   
        #SRILM feature generator
        srilm_en = SRILMFeatureGenerator("http://134.96.187.4:8585", "en" )
        #srilm_de = SRILMFeatureGenerator("http://134.96.187.4:8586", "de" )
        srilm_ngram_en = SRILMngramGenerator("http://134.96.187.4:8585", "en" )
        
        #Berkeley feature generator
        berkeley_en = BerkeleyFeatureGenerator("http://134.96.187.4:8682", "en")
        berkeley_de = BerkeleyFeatureGenerator("http://134.96.187.4:8683", "de")
        featuregenerators = [lfg, srilm_en, srilm_ngram_en, berkeley_en, berkeley_de]
        #proceed with parcing
        saxreader = SaxJCMLProcessor(output_input_file_object, featuregenerators)
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)
        input_file_object.close
        output_input_file_object.close()
    
    def analyze_external_features(self, filename, filename_out, langpair = ("de","en")):
        from featuregenerator.lengthfeaturegenerator import LengthFeatureGenerator
        from featuregenerator.parser.berkeley.parsermatches import ParserMatches
#        from featuregenerator.lm.srilm.srilmclient import SRILMFeatureGenerator
#        from featuregenerator.lm.srilm.srilm_ngram import SRILMngramGenerator
        from featuregenerator.ratio_generator import RatioGenerator
        
        input_file_object = open(filename, 'r')
        #input_file_object = codecs.open(filename, 'r', 'utf-8')
        output_input_file_object = open(filename_out, 'w')
                
        #srilm_de = SRILMFeatureGenerator("http://134.96.187.4:8586", "de" )
        #srilm_ngram_de = SRILMngramGenerator("http://134.96.187.4:8585", "de" )
        parsematches = ParserMatches(langpair)
        ratio_generator = RatioGenerator()
        lfg = LengthFeatureGenerator()  
        featuregenerators = [lfg, parsematches, ratio_generator]
        #proceed with parcing
        saxreader = SaxJCMLProcessor(output_input_file_object, featuregenerators)
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)
        input_file_object.close
        output_input_file_object.close()
        
        
    def add_diff_features(self, filename, filename_out):
        from featuregenerator.diff_generator import DiffGenerator
        dg = DiffGenerator()
        
        input_file_object = open(filename, 'r')
        output_input_file_object = open(filename_out, 'w')
        
        saxreader = SaxJCMLProcessor(output_input_file_object, [dg] )
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)
        
    
        
    
    def train_classifiers(self, filenames):
        from io_utils.input.orangereader import OrangeData
        from classifier.bayes import Bayes
        from classifier.tree import TreeLearner
        from classifier.svm import SVM
        import orange, orngLR
        if filenames[0].endswith(".tab"):
                orangetable = orange.ExampleTable(filenames[0])
                print "Passing data to Orange"
                training_data = OrangeData(orangetable)
        else:
            dataset = None
            for filename in filenames:
            
                print "Reading XML %s " % filename
                reader = XmlReader(filename)
                
                rankhandler = RankHandler()
                allow_ties = False
                parallelsentences = reader.get_parallelsentences()
                parallelsentences = rankhandler.get_pairwise_from_multiclass_set(parallelsentences, allow_ties)
                #rankhandler.get_multiclass_from_pairwise_set(parallelsentences, allow_ties)
                from featuregenerator.diff_generator import DiffGenerator
                dg = DiffGenerator()
                diff_parallelsentences = []
                for ps in parallelsentences:
                    ps = dg.add_features_parallelsentence(ps)
                    diff_parallelsentences.append(ps)
                parallelsentences = diff_parallelsentences
                
                cur_dataset = DataSet(parallelsentences)
                
                #cur_dataset =  reader.get_dataset()
                if not dataset:
                    dataset = cur_dataset
                else:
                    dataset.append_dataset(cur_dataset)
                
            class_name = "rank"
            #TODO: get list of attributes directly from feature generators
            
#            i_xmlwriter = XmlWriter(dataset)
#            i_xmlwriter.write_to_file("/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt08.pair.jcml")
#            i_xmlwriter = None
            
            
            print "Passing data to Orange"
            data = OrangeData(dataset, class_name, self.desired_attributes, self.meta_attributes, False)
            dataset=None
            
          
            
            print "Before feature subset selection (%d attributes):" %  len(data.get_data().domain.attributes)
            self.report_relevance(data.get_data())
            
#            margs = [0.1, 0.01, 0.001] 
#            for marg in margs:
#                filter = orngFSS.FilterRelief(margin=marg)
#                ndata = filter(data.get_data())
#                print "\nAfter feature subset selection with margin %5.3f (%d attributes):" % \
#                  (marg, len(ndata.domain.attributes))
#                
#                self.report_relevance(ndata)

            
            #train data
            #training_data.cross_validation()
        #training_data.print_statistics()
        # compute accuracies
        
        print "training loglinear"
        #lr = orngLR.LogRegLearner(data.get_data()) # compute classification accuracy
        print "Bayes" 
        bayes = Bayes(data)
        print "Tree"
        #tree = TreeLearner(data)
        print "SVM"
        #svm = SVM (data)
        print "knn"
        #knn = orange.kNNLearner(data.get_data(), k=10)
        
#        lr.name = "Loglinear"
        bayes.name = "bayes"
#        tree.name = "tree"
#        svm.name = "SVM"
#        lr.name = "logl"
#        knn.name = "knn"
#        
#        return [ lr, bayes, tree, svm, knn]
        return [bayes]
        
    def report_relevance(self, data):
        import orngFSS

        m = orngFSS.attMeasure(data)
        sorted(m)
        for i in m:
            print "%5.3f %s" % (i[1], i[0])
    
    
    def evaluate_sax(self, classifiers, filename, filename_out):
        input_file_object = open(filename, 'r')
        output_file_object = open(filename_out, 'w')
    
        from classifier.ranker import Ranker
        
        for classifier in classifiers:
            if classifier.name == "bayes":
                myclassifier =  classifier
        
        ranker =  Ranker(myclassifier, self.desired_attributes, self.meta_attributes)
        #proceed with parcing
        saxreader = SaxJCMLProcessor(output_file_object, [ranker])
        myparser = make_parser()
        myparser.setContentHandler(saxreader)
        myparser.parse(input_file_object)
        input_file_object.close()
        output_file_object.close()
        
    
    
    def test_classifiers(self, classifiers, filename, filename_out):
        from io_utils.input.orangereader import OrangeData
        from classifier.bayes import Bayes
        from classifier.tree import TreeLearner
        from classifier.svm import SVM
        import orange, orngLR
        reader = XmlReader(filename)
        #dataset =  reader.get_dataset()
        
        rankhandler = RankHandler()
        allow_ties = False
        parallelsentences = reader.get_parallelsentences()
        parallelsentences = rankhandler.get_pairwise_from_multiclass_set(parallelsentences, allow_ties)
        
        from featuregenerator.diff_generator import DiffGenerator
        dg = DiffGenerator()
        for i in range(len(parallelsentences)):
            parallelsentences[i] = dg.add_features_parallelsentence(parallelsentences[i])
        

            
        dataset = DataSet(parallelsentences)
        
        class_name = "rank"
        test_data = OrangeData(dataset, class_name, self.desired_attributes, self.meta_attributes)
#        (acc, taukendal) = test_data.get_accuracy(classifiers)
##        
#        print "Classification accuracies:"
#        for i in range(len(classifiers)):
#            print classifiers[i].name, "\t", acc[i], taukendal[i]
##        
#        
        for classifier in classifiers:
            if classifier.name=="bayes":
                myclassifier =  classifier
        classified_data = test_data.classify_with(myclassifier)
        parallelsentences = classified_data.get_dataset().get_parallelsentences()
        parallelsentences = rankhandler.get_multiclass_from_pairwise_set(parallelsentences, allow_ties)
        from io_utils.output.xmlwriter import XmlWriter
        classified_xmlwriter = XmlWriter(parallelsentences)
        classified_xmlwriter.write_to_file(filename_out + "xml")
        from io_utils.output.wmt11tabwriter import Wmt11TabWriter
        classified_xmlwriter = Wmt11TabWriter(parallelsentences, "dfki_parseconf")
        classified_xmlwriter.write_to_file(filename_out + "tab")
        
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
    

    ###PARTICULAR FUNCTIONS TO BE RUN ONCE
    def get_testset_trainset_wmt10(self):
        self.get_test_sentences("/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10.jcml", "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-train.jcml" , "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-test.jcml")
        
    def add_external_features_042011(self):
        #datafiles = [ "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt08.jcml"]
        datafiles = ["/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-train.jcml"]
        #datafiles = ["/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-test.jcml"]
        for datafile in datafiles:
            self.add_external_features(datafile, datafile.replace("jcml", "xf.jcml"))

        
    
    def analyze_external_features_042011(self):
        #datafiles = [ "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt08.xf.jcml"]
        datafiles = ["/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-train.jcml"]
        #datafiles.append("/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-test.xf.jcml")
        for datafile in datafiles:
            self.analyze_external_features(datafile, datafile.replace("xf.jcml", "if.jcml"))
    

    def add_diffs(self, datafiles):

        for datafile in datafiles:
            self.add_diff_features(datafile, datafile.replace("if.jcml", "diff.jcml"))    
            
    
    def convert_wmtdata(self, dir, langpair, filename):
        from io_utils.input.wmt11reader import Wmt11Reader
        reader = Wmt11Reader()
        
        writer = XmlWriter(reader.read_parallelsentences(dir, langpair))
        writer.write_to_file(filename)
        
    def jcml2wmt(self, sourcefile):
        filename_out = sourcefile.replace("jcml", "%d.tab")
        print "opening %s" % sourcefile 
        reader = XmlReader(sourcefile)
        from io_utils.output.wmt11tabwriter import Wmt11TabWriter
        
        i = 0
        filenames = []
        n = reader.length()
        while i < n:
            k = i + 100
            if k >= n:
                k = n - 1
            classified_xmlwriter = Wmt11TabWriter(None, "dfki_parseconf")
            classified_xmlwriter.write_to_file_nobuffer(filename_out % i, reader.get_parallelsentences(i, k))
            filenames.append(filename_out % i) 
            i = k + 1
        import commands
        commands.getstatusoutput("cat %s > %s" %(" ".join(filenames), sourcefile.replace("jcml", "tab") ) )
        commands.getstatusoutput("rm %s" % " ".join(filenames) )
        

if __name__ == '__main__':
    dir = getenv("HOME") + "/workspace/TaraXUscripts/data/test"
    if len(sys.argv) ==  4:
        dir = sys.argv[3]
    #add_external_features()
    #split_corpus()
    #
    
    #myexperiment = Experiment()
    
    exp = Experiment()
#    exp.add_external_features_042011()
#    exp.add_external_features_042011()
    #exp.analyze_external_features_042011()
    #exp.get_test_sentences("/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10.jcml", "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-train.jcml" , "/home/Eleftherios Avramidis/taraxu_data/wmt10-humaneval-data/wmt10-test.jcml")
    

    
    #myexperiment.add_external_features("test08.xml")
    
#    train_filename = dir + "featured_train08.xml"
#    classifiers = myexperiment.train_classifiers('/home/Eleftherios Avramidis/workspace/TaraXUscripts/src/tmpa04du_.tab')
#    #classifiers = myexperiment.train_classifiers('/home/Eleftherios Avramidis/workspace/TaraXUscripts/src/tmpa04du_.tab')
#    test_filename = dir + "featured_test08.xml"
#    myexperiment.test_classifiers(classifiers, test_filename)
    
    #===========================================================================
    #datafile = '%s/wmt10-train.partial.xf.jcml' % dir 
    #exp.analyze_external_features(datafile, datafile.replace("xf.jcml", "if.jcml"))
    #files_to_diff = ['%s/wmt08.if.jcml' % dir, '%s/wmt10-test.if.jcml' % dir, '%s/wmt10-train.partial.if.jcml' % dir ]
    #exp.add_diffs(files_to_diff)
    # 
    #===========================================================================
    #===========================================================================
    if sys.argv[1] == "train":
        classifiers = exp.train_classifiers(['%s/wmt08.if.jcml' % dir]) #,  '%s/wmt10-train.partial.if.jcml' % dir])
        exp.test_classifiers(classifiers, '%s/wmt10-test.if.jcml' % dir)
    
    elif sys.argv[1] == "ngram-features":
        sourcefile = '%s/wmt08.jcml' % dir
        targetfile = '%s/wmt08.test.jcml' % dir
        exp.add_ngram_features_batch(sourcefile, targetfile)
    
    elif sys.argv[1] == "b-features":
        sourcefile = '%s/wmt08.jcml' % dir
        targetfile = '%s/wmt08.test.jcml' % dir
        exp.add_b_features_batch(sourcefile, targetfile)
    
    elif sys.argv[1] == "readwmt":
        dir = "/home/Eleftherios Avramidis/taraxu_data/wmt11-data"
        langpair = "de-en"
        outfile = "/home/Eleftherios Avramidis/taraxu_data/wmt11-data/wmt11.jcml"
        exp.convert_wmtdata(dir, langpair, outfile)
        
    elif sys.argv[1] == "jcml2wmt":
        sourcefile = sys.argv[2]
        exp.jcml2wmt(sourcefile)
  

    elif sys.argv[1] == "wmt11fullsax":
        sourcefile = sys.argv[2]
        sys.stderr.write("\n" )
        
        print "german parser features"
        bpfile1 = sourcefile.replace("jcml", "bp.2c.jcml")
        #exp.add_b_features_batch(bpfile, bpfile1, "http://134.96.187.4:8683", "de")
        
        exp.add_external_features(sourcefile, bpfile1)
        
        print "final features"
        exfile = sourcefile.replace("jcml", "ex.3.jcml")
        exp.analyze_external_features(bpfile1, exfile) 
        
        sourcefile = sys.argv[2]
        print "classifiers"
        classifiers = exp.train_classifiers(['%s/wmt08.if.jcml' % dir]) #, '%s/wmt10-train.partial.if.jcml' %dir 
        print "testing"
        outfile = sourcefile.replace("jcml", "out.jcml")
        exp.evaluate_sax(classifiers, exfile, outfile)
        
        exp.jcml2wmt(outfile)      
    
    elif sys.argv[1] == "wmt11evalsax":
        sourcefile = sys.argv[2]
        sys.stderr.write("reading language model features" )
        sys.stderr.write("\n" )
        
        lmfile = sourcefile.replace("jcml", "lm.1.jcml")
        exp.add_ngram_features_batch(sourcefile, lmfile, "http://134.96.187.4:8585", "en")
        
        print "parser features"
        bpfile = sourcefile.replace("jcml", "bp.2.jcml")
        exp.add_b_features_batch(lmfile, bpfile, "http://134.96.187.4:8682", "en")
        #exp.add_b_features_batch(lmfile, bpfile, "http://localhost:8682", "en")
        
        print "german parser features"
        bpfile1 = sourcefile.replace("jcml", "bp.2c.jcml")
        exp.add_b_features_batch(bpfile, bpfile1, "http://134.96.187.4:8683", "de")
        
        print "final features"
        exfile = sourcefile.replace("jcml", "ex.3.jcml")
        exp.analyze_external_features(bpfile1, exfile) 
        
        sourcefile = sys.argv[2]
        print "classifiers"
        classifiers = exp.train_classifiers(['%s/wmt08.if.jcml' % dir]) #, '%s/wmt10-train.partial.if.jcml' %dir 
        print "testing"
        outfile = sourcefile.replace("jcml", "out.jcml")
        exp.evaluate_sax(classifiers, exfile, outfile)
        
        exp.jcml2wmt(outfile)
  
    
    elif sys.argv[1] == "wmt11eval":
        sourcefile = sys.argv[2]
#        
#        #print "language model features"
#        lmfile = sourcefile.replace("jcml", "lm.1.jcml")
#        #exp.add_ngram_features_batch(sourcefile, lmfile)
#        
#        print "parser features"
#        #bpfile = sourcefile.replace("jcml", "bp.2.jcml")
#        #exp.add_b_features_batch(lmfile, bpfile, "http://localhost:8682", "en")
#        
#        print "german parser features"
#        bpfile1 = sourcefile.replace("jcml", "bp.2c.jcml")
#        #exp.add_b_features_batch(bpfile, bpfile1, "http://localhost:8683", "de")
#        
#        print "final features"
        exfile = sourcefile.replace("jcml", "if.jcml")
        exp.analyze_external_features(bpfile1, exfile) 
        
        print "classifiers"
        classifiers = exp.train_classifiers(['%s/wmt08.if.jcml' % dir, '%s/wmt10-train.partial.if.jcml' %dir ])
        
        print "testing"
        outfile = sourcefile.replace("jcml", "out.jcml")
        exp.test_classifiers(classifiers, exfile, outfile)
    
    elif sys.argv[1] == "prepare_set":
        sourcefile = sys.argv[2]
        step = int(sys.argv[3])
        sys.stderr.write("reading language model features" )
        sys.stderr.write("\n" )
        
        lmfile = sourcefile.replace("jcml", "lm.1.jcml")
        if step < 2:
            exp.add_ngram_features_batch(sourcefile, lmfile, "http://134.96.187.4:8585", "en")
        
        print "parser features"
        bpfile = sourcefile.replace("jcml", "bp.2.jcml")
        if step < 3:
            exp.add_b_features_batch(lmfile, bpfile, "http://134.96.187.4:8682", "en")
        #exp.add_b_features_batch(lmfile, bpfile, "http://localhost:8682", "en")
        
        print "german parser features"
        bpfile1 = sourcefile.replace("jcml", "bp.2c.jcml")
        if step < 4:
            exp.add_b_features_batch(bpfile, bpfile1, "http://134.96.187.4:8683", "de")
        
        print "final features"
        exfile = sourcefile.replace("jcml", "ex.3.jcml")
        if step < 5:
            exp.analyze_external_features(bpfile1, exfile) 
        
        
        
    #===========================================================================