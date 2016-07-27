'''
Convert from one file format to another

Created on 7 Mar 2016

@author: elav01
'''
import argparse
from dataprocessor.qtleapcsv import QtleapCSVReader
from dataprocessor.sax.saxps2jcml import IncrementalJcml
import logging as log

READERS = {"QTleapCSV" : QtleapCSVReader}

WRITERS = {"jcml" : IncrementalJcml}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert from one format to another')
    parser.add_argument('--inputformat', help="Input format")
    parser.add_argument('--outputformat', help="Output format (default: jcml", default="jcml")
    parser.add_argument('--inputfile', help="Input file")
    parser.add_argument('--outputfile', help="Output file")
    
    args = parser.parse_args()
    
    reader_class = READERS[args.inputformat]
    reader = reader_class(args.inputfile)
    
    writer_class = WRITERS[args.outputformat]
    writer = writer_class(args.outputfile)
    
    for parallelsentence in reader.get_parallelsentences():
        writer.add_parallelsentence(parallelsentence)
    
    
    log.info("Conversion finished")