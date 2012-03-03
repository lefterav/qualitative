'''
Created on May 31, 2011

@author: elav01
'''

# To install library in ubuntu run 
# sudo apt-get install python-stdeb
# sudo pyp-install pprocess
import pprocess
from sentence.parallelsentence import ParallelSentence
from sentence.sentence import SimpleSentence
from featuregenerator.featuregenerator import FeatureGenerator

class ParallelTemplate(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """

def taketime(string):
    for i in range(2000000):
        pass
    print "done: " + string
    return string


class BerkeleyFeatureGenerator(FeatureGenerator):
    def __init__(self):
        self.attributes = []
    def get_features_tgt(self, sentence, ps):
        return {"berkeley" : taketime("BerkeleyFeatureGenerator")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentenceberkeley" : taketime(
                "parallelsentenceBerkeleyFeatureGenerator")}

class ParseMatchFeatureGenerator(FeatureGenerator):
    def get_features_tgt(self, sentence, ps):
        return {"parseMatch" : taketime("ParseMatchFeatureGenerator")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentenceparseMatch" : taketime(
                "parallelsentenceParseMatchFeatureGenerator")}

class LengthFeatureGenerator(FeatureGenerator):
    def get_features_tgt(self, sentence, ps):
        return {"length" : taketime("LengthFeatureGenerator")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentencelength" : taketime(
                "parallelsentenceLengthFeatureGenerator")}

class SRILMFeatureGenerator(FeatureGenerator):
    def get_features_tgt(self, sentence, ps):
        return {"SRILM" : sentence.get_attribute("system")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentenceSRILM" : taketime(
        "parallelsentenceSRILMFeatureGenerator")}

class RatioGenerator(FeatureGenerator):
    def get_features_tgt(self, sentence, ps):
        return {"ratio" : taketime("RatioGenerator")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentenceratio" : taketime(
                "parallelsentenceRatioGenerator")}

class DiffGenerator(FeatureGenerator):
    def get_features_tgt(self, sentence, ps):
        return {"diff" : taketime("DiffGenerator")}
    def get_features_parallelsentence(self, ps):
        return {"parallelsentencediff" : taketime(
                "parallelsentenceDiffGenerator")}
    

def run_serial(args, sentence):
    """
    Add features to the object of parallel sentence.
    @param sentence: Object of ParallelSentence()
    @type sentence: sentence.parallelsentence.ParallelSentence
    @return: Object of ParallelSentence() with added features
    @rtype: sentence.parallelsentence.ParallelSentence
    """
    for arg in args:
        sentence = arg.add_features_parallelsentence(arg(), sentence)
    return sentence


def run_parallel(parallelizedSeries, ps, nproc):
    """
    Parallelize the execution of classes that can be executed parallel. It distributes the processes on more CPUs.
    @param parallelizedSeries: list of lists of classes that can be executed parallel
    @type parallelizedSeries: list
    @param ps: empty object of parallel sentence
    @type ps: sentence.parallelsentence.ParallelSentence
    @param nproc: number of available CPUs
    @type nproc: int
    """
    results = pprocess.Map(limit=nproc, reuse=1)
    parallel_function = results.manage(pprocess.MakeReusable(run_serial))
    ps0 = ps
    n = 0
    for parallelized in parallelizedSeries:
        for args in parallelized:
            parallel_function(args, ps)
        # waits until the iteration with parallel processes is finished
        parallel_results = results[0+n:len(parallelized)+n]
        n = len(parallelized)
        
        # merge the attributes
        for ps in parallel_results:
            ps0.merge_parallelsentence(ps)
    # example in http://www.astrobetter.com/parallel-processing-in-python/


if __name__ == '__main__':

    # define series of tasks. Tasks in every generatorseries list will be
    # applied one after the other
    generatorseries1 = [BerkeleyFeatureGenerator, ParseMatchFeatureGenerator]
    generatorseries2 = [LengthFeatureGenerator]
    generatorseries3 = [SRILMFeatureGenerator]
    
    # define parallel tasks. Tasks in a parallelize lists will be run
    # in parallel
    parallelized1 = [generatorseries1, generatorseries2, generatorseries3]
    
    # serialized tasks
    generatorseries4 = [RatioGenerator]
    generatorseries5 = [DiffGenerator]
    
    # parallelized tasks
    parallelized2 = [generatorseries4, generatorseries5]
    
    # the second list of parallelized tasks, has to be run in parallel AFTER
    # the first list of parallelized tasks has finished
    parallelizedSeries = [parallelized1, parallelized2]
    
    src = SimpleSentence("I am a student")
    tgt1 = SimpleSentence("Ich bin ein Student")
    tgt1.add_attribute("system", "moses")
    tgt2 = SimpleSentence("Ich bin Student")
    tgt2.add_attribute("system", "lucy")
    ps = ParallelSentence(src, [tgt1, tgt2])
    
    nproc = 2 # maximum number of simultaneous processes desired
    
    run_parallel(parallelizedSeries, ps, nproc)
