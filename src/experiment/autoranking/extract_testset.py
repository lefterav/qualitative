'''
Created on 7 Feb 2012

@author: elav01
'''

from io.input.jcmlreader import JcmlReader
from sentence.pairwisedataset import FilteredPairwiseDataset , AnalyticPairwiseDataset
from io.sax.saxps2jcml import Parallelsentence2Jcml

def get_clean_testset(input_file, output_file):
    plain_dataset = JcmlReader(input_file)
    analytic_dataset = AnalyticPairwiseDataset(plain_dataset) 
    filtered_dataset = FilteredPairwiseDataset(analytic_dataset)
    

if __name__ == '__main__':
    