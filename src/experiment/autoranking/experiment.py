'''
Created on 23 Feb 2012

@author: lefterav
'''
from expsuite import PyExperimentSuite
from ruffus import pipeline_run
from annotate import *
from autoranking import *
from bootstrap import *
    
class Autoranking(PyExperimentSuite):
    
    def reset(self):
        pass
    
    def iterate(self):
        pass


if __name__ == '__main__':
    annotate.cfg = ExperimentConfigParser()
#cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE)
    pipeline_run([analyze_external_features])
    