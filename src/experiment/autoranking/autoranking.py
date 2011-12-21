'''
Created on 20 Oct 2011
@author: elav01
'''

from ruffus import *
import shutil
import os
from experiment.autoranking.bootstrap import cfg
from experiment.autoranking.bootstrap import get_classifier
from multiprocessing import Process, Manager 
from io.input.orangereader import OrangeData
from io.sax.saxjcml2orange import SaxJcml2Orange
from io.input.jcmlreader import JcmlReader
from io.sax.saxps2jcml import Parallelsentence2Jcml 
from sentence.dataset import DataSet
from sentence.rankhandler import RankHandler
from featuregenerator.diff_generator import DiffGenerator
from orange import ExampleTable
import cPickle as pickle
import orange
from ruffus.task import pipeline_printout_graph
from io.sax import saxjcml2orange

#TODO: Use stringIO to pass objects loaded into memory???

path = cfg.get('general','path')
try:
    os.mkdir(path)
except OSError:
    pass
os.chdir(path)

manager = Manager() 
dataset = manager.list()


def _retrieve_sentences(obj, output_file):
#    if not obj:
        return JcmlReader(output_file).get_parallelsentences()
#    elif len(obj) == 1:
#        print "got ready single object"
#        return obj.pop()
#    elif len(obj) > 1:
#        newlist = []
#        print "got many objects"
#        for i in range(len(obj)):
#            newlist.append(obj.pop())
#        return newlist


def _pass_sentences(sentences, output_file):
#    dataset.append(sentences)
    Parallelsentence2Jcml(sentences).write_to_file(output_file)

#maybe open here many files

@files(None, "trainingdata.annotated.jcml", cfg.get("training", "filename"), dataset)
def traindata_fetch(input_file, output_file, external_file, dataset):
    '''
    Fetch training file and place it comfortably in the working directory
    then load the data into memory
    '''
    shutil.copy(external_file, output_file) 
    mydataset = _retrieve_sentences(dataset, output_file)
    _pass_sentences(mydataset, output_file)

@files(None, "testdata.annotated.jcml", cfg.get("testing", "filename"), dataset)
def testdata_fetch(input_file, output_file, external_file, dataset):
    '''
    Fetch testing file and place it comfortably in the working directory
    then load the data into memory
    '''
    shutil.copy(external_file, output_file) 
    mydataset = _retrieve_sentences(dataset, output_file)
    _pass_sentences(mydataset, output_file)
    pass




@transform(traindata_fetch, suffix(".annotated.jcml"), ".pairwise.jcml", dataset, cfg.get("training", "class_name"), cfg.getboolean("preprocessing", "pairwise_exponential"), cfg.getboolean("preprocessing", "allow_ties") )
def traindata_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential, allow_ties):
    data_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential, allow_ties)
    
@transform(testdata_fetch, suffix(".annotated.jcml"), ".pairwise.jcml", dataset, cfg.get("training", "class_name"), cfg.getboolean("preprocessing", "pairwise_exponential") )
def testdata_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential):
    data_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential, True)

def data_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential, allow_ties):
    
    parallelsentences = _retrieve_sentences(dataset, input_file)
    parallelsentences = RankHandler(class_name).get_pairwise_from_multiclass_set(parallelsentences, pairwise_exponential, allow_ties)
    _pass_sentences(parallelsentences, output_file)



@transform(traindata_pairwise, suffix(".pairwise.jcml"), ".diff.jcml", dataset)
def traindata_generate_diff(input_file, output_file, dataset):
    data_generate_diff(input_file, output_file, dataset)
    
@transform(testdata_pairwise, suffix(".pairwise.jcml"), ".diff.jcml", dataset)
def testdata_generate_diff(input_file, output_file, dataset):
    data_generate_diff(input_file, output_file, dataset)    
    
def data_generate_diff(input_file, output_file, dataset):
    if not cfg.getboolean('preprocessing', 'generate_diff'):
        os.symlink(input_file, output_file)
        return
    parallelsentences = _retrieve_sentences(dataset, input_file)
    parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
    _pass_sentences(parallelsentences, output_file)


@transform(traindata_generate_diff, suffix(".diff.jcml"), ".overlap.jcml", dataset, cfg.get('training', 'class_name'))
def traindata_merge_overlapping(input_file, output_file, dataset, class_name):
    data_merge_overlapping(input_file, output_file, dataset, class_name)

@transform(testdata_generate_diff, suffix(".diff.jcml"), ".overlap.jcml", dataset, cfg.get('training', 'class_name'))
def testdata_merge_overlapping(input_file, output_file, dataset, class_name):
    data_merge_overlapping(input_file, output_file, dataset, class_name)

def data_merge_overlapping(input_file, output_file, dataset, class_name):
    if not cfg.getboolean('preprocessing', 'merge_overlapping'):
        os.symlink(input_file, output_file)
        return
    parallelsentences = _retrieve_sentences(dataset, input_file)
    parallelsentences = RankHandler(class_name).merge_overlapping_pairwise_set(parallelsentences)
    _pass_sentences(parallelsentences, output_file)
    

@transform(traindata_merge_overlapping, suffix(".overlap.jcml"), ".tab", cfg.get("training", "class_name"), cfg.get("training", "attributes").split(","), cfg.get("training", "meta_attributes").split(","), cfg.get("preprocessing", "orange_minimal"))
def traindata_get_orange(input_file, output_file, class_name, attribute_names, meta_attribute_names, orange_minimal):
    data_get_orange(input_file, output_file, class_name, attribute_names, meta_attribute_names, orange_minimal)
    
@transform(testdata_merge_overlapping, suffix(".overlap.jcml"), ".tab", cfg.get("training", "class_name"), cfg.get("training", "attributes").split(","), cfg.get("training", "meta_attributes").split(","), cfg.get("preprocessing", "orange_minimal"))
def testdata_get_orange(input_file, output_file, class_name, attribute_names, meta_attribute_names, orange_minimal):
    data_get_orange(input_file, output_file, class_name, attribute_names, meta_attribute_names, orange_minimal)

def data_get_orange(input_file, output_file, class_name, attribute_names, meta_attribute_names, orange_minimal):
    print "Starting orange conversion"
    parallelsentences = _retrieve_sentences(dataset, input_file)
    trainingset = OrangeData(DataSet(parallelsentences), class_name, attribute_names, meta_attribute_names, output_file)
    orange.saveTabDelimited ("%s.test" % output_file, trainingset.get_data())

    #SaxJcml2Orange(input_file, class_name, attribute_names, meta_attribute_names, output_file)
    print "Finished orange conversion"
    pass
    #dataset.append(trainingset_orng) #EOF error thrown given when used
    

def _get_continuizer_constant(name):
    return getattr(orange.DomainContinuizer, name)

@transform(traindata_get_orange, suffix(".tab"), ".clsf" , cfg.getboolean("training", "continuize"), cfg.get("training", "multinomialTreatment"), cfg.get("training", "continuousTreatment"), cfg.get("training", "classTreatment"))
def train_classifier(input_file, output_file, param_continuize, multinomialTreatment, continuousTreatment, classTreatment):
    #fetch data the fastest way
    #try:
    #    trainingset_orng = dataset.pop()
    #except:
    #    trainingset_orng = ExampleTable(input_file)
    trainingset_orng = ExampleTable(input_file)
    print "Loaded ", len(trainingset_orng) , " sentences from file " , input_file
    trainingset_dataset = OrangeData(trainingset_orng).get_dataset()
    
    #prepare classifeir params
    classifier_params = {"multinomialTreatment" : _get_continuizer_constant(cfg.get("training", "multinomialTreatment")),
                         "continuousTreatment" : _get_continuizer_constant(cfg.get("training", "continuousTreatment")),
                         "classTreatment" : _get_continuizer_constant(cfg.get("training", "classTreatment"))}
                                                                                               
    #train the classifier
    classifier = get_classifier() #fetch classifier object

    try:    
        myclassifier = classifier()   #initialize it
        trained_classifier = myclassifier.learnClassifier(trainingset_orng, classifier_params)
    except:
        trained_classifier = classifier(OrangeData(trainingset_orng))
    objectfile = open(output_file, 'w')
    pickle.dump(trained_classifier, objectfile)
    objectfile.close()
    #dataset.append(trained_classifier)



@merge([train_classifier, testdata_get_orange], "testdata.classified.tab")
def test_classifier(infiles, output_file):
    #load classifier 
    classifier_filename = infiles[0]
    classifier_file = open(classifier_filename, 'r')
    trained_classifier = pickle.load(classifier_file) 
    classifier_file.close()
    print "classifier loaded"
    #load testdata
    testset_orng = OrangeData(ExampleTable(infiles[1]))
    
    classified_orng = testset_orng.classify_with(trained_classifier)
#    orange.saveTabDelimited (output_file, classified_orng.get_data())
#@transform(test_classifier, suffix("tab"), ".jcml")
#def test_deorange(input_file, output_file):
#    testset_orng = ExampleTable(input_file)
#    dataset = OrangeData(testset_orng).get_dataset()
    dataset = classified_orng.get_dataset()
    Parallelsentence2Jcml(dataset.get_parallelsentences()).write_to_file(output_file)


@transform(test_classifier, suffix("classified.jcml"), cfg.get('training', 'class_name') )
def test_revert_multiclass(input_file, output_file, class_name ):
    if not cfg.getboolean('preprocessing', 'pairwise'):
        os.symlink(input_file, output_file)
        return
    classified_dataset = JcmlReader(input_file).get_dataset()
    allow_ties = True
    parallelsentences_multiclass = RankHandler(class_name).get_multiclass_from_pairwise_set(classified_dataset, allow_ties)
    Parallelsentence2Jcml(parallelsentences_multiclass).write_to_file(output_file)


    


    
#maybe merge here



pipeline_printout_graph("flowchart.jpg", "jpg", [test_revert_multiclass])
pipeline_run([test_revert_multiclass], multiprocess = 1)



#class ExpDataReader(AccumulativeTask):
    
#    def execute(self):
        


#class Autoranking:
    
#    def define(self):
#        executable = []
#        training_data_reader = ExpDataReader(inputfilenames = self.training_filenames)
#        executable.append(training_data_reader) #dataset object and jcmlfile
#        
#        training_data_pairwiser = ExpDataPairwiser(input = training_data_reader) #pairwise dataset object and jcmlfile
#        training_data_converter = ExpDataOrangeConverter(input = training_data_pairwiser) #orange object and tab file
#        classifier_trainer = ExpClassifierTrainer(input = training_data_converter) #classifier object and pickle
#        
#        test_data_reader = ExpDataReader(inputfilenames = self.testing_filenames)        
        
#        test_data_pairwiser = ExpDataPairwiser(input = test_data_reader) #pairwise dataset object and jcmlfile
        
#        test_data_converter = ExpDataOrangeConverter(input = test_data_pairwiser) #orange object and tab file
        
#        classifier_tester = ExpClassifierTester(classifier = classifier_trainer, input = test_data_converter)
#        results_analyzer = ResultsAnalyzer(results = classifier_tester, input = test_data_reader)
        
        



#if __name__ == '__main__':
#    pass