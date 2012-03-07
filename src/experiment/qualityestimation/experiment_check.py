'''
Created on 07 Mar 2012

@author: lefterav
'''

from suite import QualityEstimationSuite
import argparse 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display progress of variable')
    
    mysuite = QualityEstimationSuite()
    a = mysuite.get_values_fix_params("./19/quality_estimation_development", 0, "RootMeanSqrErr")
    b = mysuite.get_values_fix_params("./19/quality_estimation_development", 0, "MeanAvgErr")
    for entry in zip(a[0], b[0] , ["%s-%s" % (i['classifier'], i['att']) for i in a[1]]):
        print entry
