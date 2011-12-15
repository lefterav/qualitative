'''
Created on 20 Oct 2011

@author: elav01
'''

from ruffus import *
import shutil
import os
from experiment.autoranking.bootstrap import cfg
from multiprocessing import Process, Manager 
from io.input.jcmlreader import JcmlReader
from io.sax.saxps2jcml import Parallelsentence2Jcml 
from sentence.rankhandler import RankHandler
from featuregenerator.diff_generator import DiffGenerator


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
    if not obj:
        return JcmlReader(output_file).get_parallelsentences()
    else:
        print "got ready object"
        return obj[0]

def _pass_sentences(sentences, output_file):
    dataset.append(sentences)
    Parallelsentence2Jcml(sentences).write_to_file(output_file)


#maybe open here many files

@files(None, "data.raw", cfg.get("training", "filename"), dataset)
def data_fetch(input_file, output_file, external_file, dataset):
    '''
    Fetch file and place it comfortably in the working directory
    then load the data into memory
    '''
    shutil.copy(external_file, output_file) 
    dataset = _retrieve_sentences(dataset, output_file)
    _pass_sentences(dataset, output_file)



@active_if(cfg.getboolean('training', 'pairwise'))
@transform(data_fetch, suffix(".raw"), ".pairwise", dataset, cfg.get("training", "class_name"), cfg.getboolean("training", "pairwise_exponential"), cfg.getboolean("training", "allow_ties") )
def data_pairwise(input_file, output_file, dataset, class_name, pairwise_exponential, allow_ties):
    parallelsentences = _retrieve_sentences(dataset, input_file)
    print "got sentences"
    parallelsentences = RankHandler(class_name).get_pairwise_from_multiclass_set(parallelsentences, pairwise_exponential, allow_ties)
    print "converted"
    print "writing to output ", output_file
    _pass_sentences(parallelsentences, output_file)
    print "written down"


@active_if(cfg.getboolean('training', 'generate_diff'))
@transform(data_pairwise, suffix(".pairwise"), ".diff", dataset)
def data_generate_diff(input_file, output_file, dataset):
    parallelsentences = _retrieve_sentences(dataset, input_file)
    parallelsentences = DiffGenerator().add_features_batch(parallelsentences)
    _pass_sentences(parallelsentences)


#maybe merge here

@active_if(cfg.getboolean('training', 'merge_overlapping'))
@transform(data_generate_diff, suffix(".diff"), ".merge", dataset, cfg.get('training', 'class_name'))
def data_merge_overlapping(input_file, output_file, dataset, class_name):
    parallelsentences = _retrieve_sentences(dataset, input_file)
    parallelsentences = RankHandler(class_name).merge_overlapping_pairwise_set(parallelsentences)

pipeline_run([data_pairwise], [data_fetch], multiprocess = 1)


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