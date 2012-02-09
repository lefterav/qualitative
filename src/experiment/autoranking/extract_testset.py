'''
Created on 7 Feb 2012

@author: elav01
'''

from io.input.jcmlreader import JcmlReader
from sentence.pairwisedataset import FilteredPairwiseDataset
from io.sax.saxps2jcml import Parallelsentence2Jcml

def get_clean_testset(input_file, output_file):
    plain_dataset = JcmlReader(input_file)
    filtered_dataset = FilteredPairwiseDataset(plain_dataset)
    

if __name__ == '__main__':
    