'''
Created on 23 Feb 2012

@author: lefterav
'''

import os
import shutil
from ruffus import pipeline_run

class Experiment:
    pass

if __name__ == '__main__':
    
    import annotate
    
#cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE)
    pipeline_run([annotate.analyze_external_features])
    