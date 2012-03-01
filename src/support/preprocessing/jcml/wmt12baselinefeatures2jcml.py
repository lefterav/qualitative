'''
Created on 1 Mar 2012

@author: elav01
'''

import sys
from io.sax.saxps2jcml import Parallelsentence2Jcml
from io.input.jcmlreader import JcmlReader
from xml.etree import ElementTree

def wmt12baselinefeatures2jcml(features_description_filename, features_filename, input_jcml, output_jcml):
    attribute_names = read_attribute_names(features_description_filename)
    att_vector = get_attribute_vector(attribute_names, features_filename)
    
    existing_dataset = JcmlReader(input_jcml).get_dataset()
    existing_dataset.add_attribute_vector(att_vector, "ps")
    Parallelsentence2Jcml(existing_dataset).write_to_file(output_jcml)

    
def get_attribute_vector(attribute_names, features_filename):  
    f = open(features_filename, 'r')
    att_vector = [] 
    
    for line in f:
        values = line.split('\t')
        atts = dict([(k, v) for k,v in zip(attribute_names, values)])
        att_vector.append(atts)
    
    f.close()      
    return att_vector
 
    
def read_attribute_names(features_description_filename):
    tree = ElementTree.parse(features_description_filename)
    feature_elements = tree.findall("feature")    
    return ["bb_{0}".format(f.get("index")) for f in feature_elements]


if __name__ == '__main__':
    features_description_filename = sys.argv[1]
    features_filename = sys.argv[2]
    input_jcml = sys.argv[3]
    output_jcml = sys.argv[4]
    wmt12baselinefeatures2jcml(features_description_filename, features_filename, input_jcml, output_jcml)
    
    