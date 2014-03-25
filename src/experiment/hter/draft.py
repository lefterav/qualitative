'''
Created on 25 Mar 2014
@author: Eleftherios Avramidis
'''
import sys
import yaml
from io_utils.sax.utils import join_jcml, CEJcmlReader
from ml.lib.scikit.scikit import SkRegressor
import logging as log

#todo: this should be read from config file (or expsuite)
cfg_path = "/home/elav01/workspace/qualitative/src/experiment/hter/config/svr.cfg"
class_name = "score"
desired_parallel_attributes = []
desired_source_attributes = []
desired_target_attributes = []
meta_attributes = []

if __name__ == '__main__':
    
    #load and join filenames
    input_filenames = sys.argv[1:]
    print "Input filenames:", input_filenames
    input_xml_filename = "train.jcml"
    join_jcml(input_filenames, input_xml_filename)
    dataset = CEJcmlReader(input_xml_filename)
    
    #logging
    log.basicConfig(level=log.DEBUG)
    
    # open the config file
    config = None
    with open(cfg_path, "r") as cfg_file:
        config = yaml.load(cfg_file.read())
         
    #initialize the regressor
    regressor = SkRegressor(config)
    log.info("Loading data")
    regressor.load_training_dataset(dataset, class_name, desired_parallel_attributes, desired_source_attributes, desired_target_attributes, meta_attributes)
    regressor.set_learning_method()
    log.info("Performing cross validation")
    print regressor.cross_validate_start()
    
    
    