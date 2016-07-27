'''
Provide statistics for particular features from JCML files
Created on 22 Jul 2014

@author: Eleftherios Avramidis
'''

from dataprocessor.ce.cejcml import get_statistics
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Provide statistics for particular features from JCML files")
    parser.add_argument('--files', metavar='FILES', nargs='+', help="The JCML files to be parsed for calculating feature statistics")
    parser.add_argument('--all',  help="Get statistics for all features", nargs='?')
    parser.add_argument('--parallel', metavar='PAR_FEATURES', nargs='*', help="The names of the parallel sentence features whose statistics will be calculated")
    parser.add_argument('--src', metavar='SRC_FEATURES', nargs='*', help="The names of the source features whose statistics will be calculated")
    parser.add_argument('--tgt', metavar='TGT_FEATURES', nargs='*', help="The names of the target features whose statistics will be calculated")
    parser.add_argument('--ref', metavar='REF_FEATURES', nargs='*', help="The names of the reference features whose statistics will be calculated")
    args = parser.parse_args() 
    
    if args.all:
        for line in get_statistics(args.files,
                                    all_general =  True,
                                    all_target = True,
                                     
                                    #desired_general=args.parallel,
                                    #desired_source=args.src,
                                    #desired_target=args.tgt,
                                    #desired_ref=args.ref)
                                    ):
             print line
    
    
       
