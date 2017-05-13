'''
Created on May 13, 2017

@author: lefterav
'''
from dataprocessor.ce.cejcml import CEJcmlReader
from sentence.sentence import SimpleSentence
import sys

def convert_jcmlfeatures2tab(in_jcml_filename, out_tab_filename, attribute_names):
    reader = CEJcmlReader(in_jcml_filename, desired_target=attribute_names)
    for parallelsentence in reader.get_parallelsentences():
        sentence_featurevector = []
        for translation in parallelsentence.get_translations():
            translation = SimpleSentence()
            featurevector = translation.get_vector(attribute_names, default_value=0, replace_infinite=True, replace_nan=True)
            sentence_featurevector.append(featurevector)
        print "\t".join([str(v) for v in sentence_featurevector])         

if __name__ == '__main__':
    
    
    attribute_names = open(sys.argv[3]).read().split(",")
    convert_jcmlfeatures2tab(sys.argv[1], sys.argv[2], attribute_names)