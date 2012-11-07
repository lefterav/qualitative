'''
Created on 7 Nov 2012

@author: elav01
'''

import sys

if __name__ == '__main__':
    
    filename = sys.argv[1]
    train_output_filename = sys.argv[2]
    test_output_filename = sys.argv[3]
    percentage = float(sys.argv[4])    
    
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
    
    sys.stderr("Writing training sentences")
    f = open(train_output_filename, 'w')
    for training_line in lines[:training_len]:
        f.write(training_line)
        f.write('\n')
    f.close()
    
    sys.stderr("Writing test sentences")
    f = open(test_output_filename, 'w')
    
    for testline in valid_test_lines:
        f.write(testline)
        f.write('\n')

    f.close()