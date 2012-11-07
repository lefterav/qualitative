'''
Created on 7 Nov 2012

@author: elav01
'''

import sys

if __name__ == '__main__':
    
    filename = sys.argv[1]
    percentage = float(sys.argv[2])
    
    
    f = open(filename, 'r')
    lines = [l.strip() for l in f.readlines()]
    f.close()
    
    target_test_len = int(percentage * len(lines))
    training_len = len(lines) - target_test_len
    valid_test_lines = []
    
    
    while valid_test_lines < target_test_len:
        sys.stderr.write("I already have {} test lines, whereas the aim is {}. Trainset will contain {} sentences\n".format(len(valid_test_lines), target_test_len, training_len))
        
        for test_line in lines[training_len+1:]:
            test_line_valid = True
            for training_line in lines[:training_len]:
                if training_line == test_line:
                    test_line_valid = False
                    break
            if test_line_valid:
                valid_test_lines.append(test_line)
        
        training_len = training_len - 10
        
        
                
        
    
    pass

