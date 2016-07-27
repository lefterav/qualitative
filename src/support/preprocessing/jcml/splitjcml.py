'''
Created on 24 Oct 2012

@author: Eleftherios Avramidis
'''

from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml
from dataprocessor.input.jcmlreader import JcmlReader
from sys import argv
import sys

def split_dataset_files(source_xml_file, target_file_1, target_file_2, ratio=0.1):
    sys.stderr.write("Reading source file %s ...\n"% source_xml_file)
    source_dataset = JcmlReader(source_xml_file).get_dataset()
    dataset_part1, dataset_part2 = source_dataset.split(ratio)
    sys.stderr.write("Writing first target file %s ...\n"% target_file_1)
    Parallelsentence2Jcml(dataset_part1).write_to_file(target_file_1)
    sys.stderr.write("Writing second target file %s ...\n"% target_file_2)
    Parallelsentence2Jcml(dataset_part2).write_to_file(target_file_2)

if __name__ == '__main__':

    ratio = 0.1
    if len(argv) == 5:
        ratio = float(argv[4])
    split_dataset_files(argv[1], argv[2], argv[3], ratio)


    
