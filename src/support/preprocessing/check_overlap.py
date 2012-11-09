'''
Created on 9 Nov 2012

@author: elav01
'''

import sys

if __name__ == '__main__':
    file1 = open(sys.argv[1], 'r')
    file2 = open(sys.argv[2], 'r')
    
    matched = []
    for line1 in file1:
        i=0
        for line2 in file2:
            print ".",
            if line1 == line2:
                matched.append(i) 
            i+=1
    print matched