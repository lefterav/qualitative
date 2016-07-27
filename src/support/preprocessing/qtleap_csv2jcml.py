'''
Convert from QTleap CSV format to another

Created on 7 Mar 2016

@author: elav01
'''
import argparse
from dataprocessor.qtleapcsv import QtleapCSVReader
from dataprocessor.sax.saxps2jcml import IncrementalJcml
import logging as log

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert from one format to another')
    parser.add_argument('--inputfile', help="Input file")
    parser.add_argument('--sourcefile', help="Plain text file with source sentences")
    parser.add_argument('--outputfile', help="Output file")
    
    args = parser.parse_args()
    
    reader = QtleapCSVReader(args.inputfile, sourcefile=args.sourcefile)
    writer = IncrementalJcml(args.outputfile)
    
    for parallelsentence in reader.get_parallelsentences():
        writer.add_parallelsentence(parallelsentence)
    
    log.info("Conversion finished")