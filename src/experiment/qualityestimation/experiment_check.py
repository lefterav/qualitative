'''
Created on 07 Mar 2012

@author: lefterav
'''

from suite import QualityEstimationSuite
import argparse 
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display progress of variable')

    directory = sys.argv[1]
    
    mysuite = QualityEstimationSuite()
    a = mysuite.get_values_fix_params("./%s" % directory , 0, "RootMeanSqrErr")
    b = mysuite.get_values_fix_params("./%s" % directory, 0, "MeanAvgErr")
    for entry in zip(a[0], b[0] , ["%s-%s" % (i['classifier'], i['att']) for i in a[1]]):
        print entry
