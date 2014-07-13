'''
Created on 23 Feb 2012

@author: Eleftherios Avramidis
'''

import os
import shutil
from ruffus import pipeline_run
import annotate

class Experiment:
    pass

if __name__ == '__main__':
    pipeline_run([annotate.analyze_external_features])
    