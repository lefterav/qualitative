'''
Created on 20 Oct 2011

@author: elav01
'''


class ExpDataReader(AccumulativeTask):
    
    def execute(self):
        


class Autoranking:
    
    def define(self):
        executable = []
        training_data_reader = ExpDataReader(inputfilenames = self.training_filenames)
        #executable.append(training_data_reader) #dataset object and jcmlfile
        
        training_data_pairwiser = ExpDataPairwiser(input = training_data_reader) #pairwise dataset object and jcmlfile
        training_data_converter = ExpDataOrangeConverter(input = training_data_pairwiser) #orange object and tab file
        classifier_trainer = ExpClassifierTrainer(input = training_data_converter) #classifier object and pickle
        
        test_data_reader = ExpDataReader(inputfilenames = self.testing_filenames)        
        
        test_data_pairwiser = ExpDataPairwiser(input = test_data_reader) #pairwise dataset object and jcmlfile
        
        test_data_converter = ExpDataOrangeConverter(input = test_data_pairwiser) #orange object and tab file
        
        classifier_tester = ExpClassifierTester(classifier = classifier_trainer, input = test_data_converter)
        results_analyzer = ResultsAnalyzer(results = classifier_tester, input = test_data_reader)
        
        



if __name__ == '__main__':
    pass