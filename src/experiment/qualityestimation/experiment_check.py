'''
Created on 07 Mar 2012

@author: lefterav
'''

from suite import QualityEstimationSuite
import argparse 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display progress of variable')
    
    mysuite = QualityEstimationSuite()
    mysuite.get_values_fix_params("quality_estimation_development", 0, "RootMeanSqrErr")
    mysuite.get_values_fix_params("quality_estimation_development", 0, "MeanAvgErr")