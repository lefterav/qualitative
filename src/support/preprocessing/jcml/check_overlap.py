'''
Check overlap between two XML files originating from WMT
Created on Jul 12, 2016

@author: elav01
'''

import sys
from dataprocessor.ce.cejcml import CEJcmlReader

def check_overlap(bigfilename, smallfilename):
    bigfile = CEJcmlReader(bigfilename)
    smallfile = CEJcmlReader(smallfilename)
    small_ids = set([p.get_safe_id_tuple() for p in smallfile])
    
    for parallelsentence in bigfile:
        big_id = parallelsentence.get_safe_id_tuple()
        if big_id in small_ids:
            print big_id         
    


if __name__ == '__main__':
    check_overlap(sys.argv[1], sys.argv[2])
