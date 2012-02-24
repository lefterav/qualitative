'''
Created on 23 Feb 2012

@author: lefterav
'''

from io.input.jcmlreader import JcmlReader
from sentence.coupleddataset import CoupledDataSet
from io.sax.saxps2jcml import Parallelsentence2Jcml

if __name__ == '__main__':
    
    input_file = "/home/lefterav/taraxu_data/wmt12/qe/training_set/traning.jcml"
    output_file = "/home/lefterav/taraxu_data/wmt12/qe/training_set/traning.coupled.jcml"
    simple_dataset = JcmlReader(input_file).get_dataset()
    coupled_dataset = CoupledDataSet(simple_dataset)
    Parallelsentence2Jcml(coupled_dataset.get_parallelsentences()).write_to_file(output_file)
    