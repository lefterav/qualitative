'''
Created on 7 Feb 2012

@author: elav01
'''

from io_utils.input.jcmlreader import JcmlReader
from sentence.pairwisedataset import FilteredPairwiseDataset , AnalyticPairwiseDataset
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
import os

def get_clean_testset(input_file, output_file):
    plain_dataset = JcmlReader(input_file).get_dataset()
#    plain_dataset.remove_ties()
    analytic_dataset = AnalyticPairwiseDataset(plain_dataset) 
    filtered_dataset = FilteredPairwiseDataset(analytic_dataset, 1.00)
    filtered_dataset.remove_ties()
    reconstructed_dataset = filtered_dataset.get_multiclass_set()
    reconstructed_dataset.remove_ties()
    Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences()).write_to_file(output_file)


if __name__ == '__main__':
    langpairs = ["de-en", "en-de", "en-fr", "fr-en", "en-es", "es-en", "en-cz", "cz-en"]
    sets = ['wmt2008', 'wmt2009', 'wmt2010', 'wmt2010-public', "wmt2011.combo"]
    for setid in sets:
        for langpair in langpairs:
            input_filename = "/home/elav01/taraxu_data/jcml-latest/raw/%s.%s.jcml.rank.jcml" % (setid, langpair)
            print input_filename
            output_filename = "/home/elav01/taraxu_data/jcml-latest/clean/%s.%s.rank-clean.jcml" % (setid, langpair)
            get_clean_testset(input_filename, output_filename)