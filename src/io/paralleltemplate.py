'''
Created on May 31, 2011

@author: elav01
'''

# To install library in ubuntu run 
# sudo apt-get install python-stdeb
# sudo pyp-install pprocess
import pprocess


def taketime():
    #write a function that consumes time without doing anything
    pass

class ParallelSentence:
    def __init__(self):
        self.attributes = []
    def add_features(self, features):
        self.attributes.extend(features)
    pass


class BerkeleyFeatureGenerator:
    def get_features(self):
        taketime()
        return None

# define functions for all the Feature Generators below, that call the taketime function and print their name  


#Before reading this, read the main function below
def run_parallel(parallelizedseries):
    #use example in http://www.astrobetter.com/parallel-processing-in-python/
    sentence = ParallelSentence()
    sentence.add_features(generatorseries1[0].get_features[sentence])
    sentence.add_features(generatorseries1[1].get_features[sentence])
    #make this serialized, then parallelize over the next list
    
    
    
    pass

    


if __name__ == '__main__':
    
    
    #define series of tasks. Tasks in every generatorseries list will be applied one after the other
    generatorseries1 = [BerkeleyFeatureGenerator, ParseMatchFeatureGenerator]
    generatorseries2 = [LengthFeatureGenerator]
    generatorseries3 = [SRILMFeatureGenerator]
    
    #define parallel tasks. Tasks in a parallelize lists will be run in parallel
    parallelize1 = [generatorseries1, generatorseries2, generatorseries3]
    
    #serialized tasks
    generatorseries4 = [RatioGenerator]
    generatorseries5 = [DiffGenerator]
    
    #parallelized tasks
    parallelize2 = [generatorseries4, generatorseries5]
    
    #the second list of parallelized tasks, has to be run in parallel AFTER the first list of parallelized tasks has finished
    parallelizedseries = [parallelized1, parallelized2]
    
    
    self.run_parallel(parallelizedseries)
    
    
    
    
    