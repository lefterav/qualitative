'''
Created on May 31, 2013

@author: Eleftherios Avramidis
'''

from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
import sys


if __name__ == '__main__':
    dataset = None
    for filename in sys.argv[2:]:
        newdataset = JcmlReader(filename).get_dataset()
        if dataset:
            dataset.append_dataset(newdataset)
        else:
            dataset = newdataset
    Parallelsentence2Jcml(dataset).write_to_file(sys.argv[1])
    
        