'''
Created on 20 Oct 2011

@author: elav01
'''

from ruffus import *
import shutil
import os
from io.input.jcmlreader import JcmlReader
from sentence.rankhandler import RankHandler

from experiment.autoranking.bootstrap import cfg

#TODO: Use stringIO to pass objects loaded into memory???

path = cfg.get('general','path')
try:
    os.mkdir(path)
except OSError:
    pass
os.chdir(path)

dataset = [None]

def _retrieve_sentences(obj, output_file):
    if obj == [None]:
        return JcmlReader(output_file).get_parallelsentences()
    else:
        return obj


@files(None, 'data.input.jcml', cfg.get('training', 'filename'), dataset)
def data_fetch(input_file, output_file, external_file, dataset):
    '''
    Fetch file and place it comfortably in the working directory
    then load the data into memory
    '''
    shutil.copy(external_file, output_file)
    dataset[0] = _retrieve_sentences(dataset, output_file)

#@active_if(True)
@files(data_fetch, 'data.pairwise.jcml', dataset)
def data_pairwise(input_file, output_file, dataset, cfg.get('training', )):
    print input_file
    print "received dataset with value" , dataset
    RankHandler(self.class_name).get_pairwise_from_multiclass_set(parallelsentences, allow_ties, self.exponential)
    


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