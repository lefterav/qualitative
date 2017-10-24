'''
Created on Jun 17, 2016

@author: lefterav
'''
from dataprocessor.ce.cejcml import CEJcmlReader

def tau_ties(filename):
    testset = CEJcmlReader(filename)
    for parallelsentence in testset:
        ranking = parallelsentence.get_ranking()

if __name__ == '__main__':
    pass