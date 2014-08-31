'''
Created on 7 Feb 2012

@author: Eleftherios Avramidis
'''

from dataprocessor.input.jcmlreader import JcmlReader
from sentence.pairwisedataset import FilteredPairwiseDataset , AnalyticPairwiseDataset
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
import os
import argparse
from ConfigParser import ConfigParser

def get_clean_testset(input_file, output_file):
    plain_dataset = JcmlReader(input_file).get_dataset()
#    plain_dataset.remove_ties()
    analytic_dataset = AnalyticPairwiseDataset(plain_dataset) 
    filtered_dataset = FilteredPairwiseDataset(analytic_dataset, 1.00)
    filtered_dataset.remove_ties()
    reconstructed_dataset = filtered_dataset.get_multiclass_set()
    reconstructed_dataset.remove_ties()
    Parallelsentence2Jcml(reconstructed_dataset.get_parallelsentences(), shuffle_translations=True).write_to_file(output_file)


if __name__ == '__main__':
    
    langpairs = ["de-en", 
                 "en-de", 
                 "en-fr", 
                 "fr-en", 
                 "en-es", 
                 "es-en", 
                 "en-cz", 
                 "cz-en"
                ]
    
    sets = ['wmt2008', 'wmt2009', 'wmt2010', 'wmt2010-public', "wmt2011.newstest", "wmt2011.combo"]

    cfg = ConfigParser()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--langpair", nargs='*', default=langpairs, help="Language pairs")
    parser.add_argument("--setid", nargs='*', default=sets, help="set names")
    parser.add_argument("--input", help="input file pattern, e.g. /home/Eleftherios Avramidis/taraxu_data/jcml-latest/raw/{setid}.{langpair}.jcml.rank.jcml")
    parser.add_argument("--output", help="output file pattern, e.g. /home/Eleftherios Avramidis/taraxu_data/jcml-latest/clean/{setid}.{langpair}.jcml.rank.jcml")
    args = parser.parse_args()
    
    for setid in args.setid:
        for langpair in args.langpair:
            input_xml_filename = args.input.format(setid=setid, langpair=langpair)
            output_filename = args.output.format(setid=setid, langpair=langpair)
            get_clean_testset(input_xml_filename, output_filename)