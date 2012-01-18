'''
Created on 17 Jan 2012

@author: lefterav
'''



import shutil
import os

#pipeline essentials
from ruffus import *
from multiprocessing import Process, Manager 
from ruffus.task import pipeline_printout_graph
import cPickle as pickle

#internal code classes
from experiment.autoranking.bootstrap import cfg
from experiment.autoranking.bootstrap import get_classifier
from io.input.orangereader import OrangeData
from io.sax.saxjcml2orange import SaxJcml2Orange
from io.input.jcmlreader import JcmlReader
from io.sax import saxjcml2orange
from io.sax.saxps2jcml import Parallelsentence2Jcml 
from sentence.dataset import DataSet
from sentence.rankhandler import RankHandler
from featuregenerator.diff_generator import DiffGenerator
from sentence.scoring import Scoring

#ML
from orange import ExampleTable
import orange

import re



@split(None, "*original.jcml", cfg.get("annotation", "filenames").split(","))
def data_fetch(input_file, output_files, external_files):
    '''
    Fetch training file and place it comfortably in the working directory
    then load the data into memory
    '''
    for external_file in external_files:
        print "Moving here external file ", external_file
        (path, setname) = re.findall("(.*)/([^/]*)\.jcml", external_file)[0]
        
        output_file = "%s.%s" % (setname, "original.jcml")
        shutil.copy(external_file, output_file)


def features_parse():
    pass

def features_parse_source():
    pass

def features_parse_target():
    pass

def features_lm():
    pass

def features_lm_source():
    pass

def features_lm_target():
    pass

def analyze_external_features():
    pass

def features_gather():
    pass



       

if __name__ == '__main__':
    pass