'''
Created on 25 Mar 2014
@author: Eleftherios Avramidis
'''
import sys
import yaml
from io_utils.sax.utils import join_jcml, CEJcmlReader
from io_utils.input.jcmlreader import JcmlReader
from ml.lib.scikit.scikit import SkRegressor
import logging as log

#todo: this should be read from config file (or expsuite)
cfg_path = "/home/elav01/workspace/qualitative/src/experiment/hter/config/svr.cfg"
class_name = "ter_substitutions"
desired_parallel_attributes = []
desired_source_attributes = []
desired_target_attributes = ["q_1022_1","q_1012_1","q_1015_1","q_1001_1","q_1002_1","q_1006_1","q_1036_1","q_1009_1","q_1057_1","q_1054_1","q_1053_1","q_1050_1","q_1049_1"]
#"q_1075_1","q_1074_1",,"q_1046_1"
#["qb_1022","qb_1012","qb_1015","qb_1001","qb_1002","qb_1006","qb_1036","qb_1009","qb_1057","qb_1054","qb_1053","qb_1050","qb_1049","qb_1075","qb_1074","qb_1046"]


meta_attributes = []

if __name__ == '__main__':
    
    #load and join filenames
    log.info("Creating joined file")
    input_filenames = sys.argv[1:]
    print "Input filenames:", input_filenames
    input_xml_filename = "train.jcml"
    join_jcml(input_filenames, input_xml_filename)
#    dataset = JcmlReader(input_xml_filename)
    dataset = CEJcmlReader(input_xml_filename, all_general=True, all_target=True)
    
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
    scores = regressor.cross_validate_start(cv=5)
    print scores
    
    
    
