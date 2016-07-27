'''
Created on May 31, 2013

@author: Eleftherios Avramidis
'''

from dataprocessor.ce.utils import join_jcml
import sys

if __name__ == '__main__':
    filenames = sys.argv[2:]
    output_filename = sys.argv[1]
    join_jcml(filenames, output_filename)
    