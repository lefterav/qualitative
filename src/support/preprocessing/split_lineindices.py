'''
Created on Oct 29, 2013

@author: Eleftherios Avramidis
'''

import sys

if __name__ == '__main__':
    
    filename_original = sys.argv[1]
    filename_indices = sys.argv[2]
    filename_output_1 = "../split/{}.1".format(filename_original)
    filename_output_2 = "../split/{}.2".format(filename_original)
    
    file_original = open(filename_original, 'r')
    file_indices = open(filename_indices, 'r')
    file_output_1 = open(filename_output_1, 'w')
    file_output_2 = open(filename_output_2, 'w')
    
    i = 1 
    
    indices = [int(index) for index in file_indices.readlines()]
    
    for line in file_original:
        if i in indices:
            print ">"
            file_output_1.write(line)
        else:
            print "<"
            file_output_2.write(line)
        
        i+=1
        
    file_original.close()
    file_indices.close()
    file_output_1.close()
    file_output_2.close()
        
    
    
