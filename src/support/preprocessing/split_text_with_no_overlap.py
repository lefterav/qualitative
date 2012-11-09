'''
Created on 7 Nov 2012

@author: elav01
'''

import sys, argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--inputstem')
    parser.add_argument('--sourcelang')
    parser.add_argument('--targetlang')
    parser.add_argument('--trainstem')    
    parser.add_argument('--teststem')
    parser.add_argument('--percentage')
    
    args = parser.parse_args()
    
    source_filename = args.inputstem + "." + args.sourcelang
    target_filename = args.inputstem + "." +  args.targetlang
    source_training_filename = args.trainstem + "." + args.sourcelang
    target_training_filename = args.trainstem + "." + args.targetlang
    source_test_filename = args.teststem + "." + args.sourcelang
    target_test_filename = args.teststem + "." + args.targetlang
    
    f = open(source_filename, 'r')
    sourcelines = [l.strip() for l in f.readlines()]
    f.close()
    
    f = open(target_filename, 'r')
    targetlines = [l.strip() for l in f.readlines()]
    f.close()
    
    assert(len(sourcelines)==len(targetlines))
    
    target_test_len = int(float(args.percentage) * len(sourcelines))
    training_len = len(sourcelines) - target_test_len

    source_valid_test_lines = []
        
    while len(source_valid_test_lines) < target_test_len:
        sys.stderr.write("I already have {} test lines, whereas the aim is {}. Trainset will contain {} sentences\n".format(len(source_valid_test_lines), target_test_len, training_len))
        filtered_count = 0
        source_valid_test_lines = []
        target_valid_test_lines = []
        
        source_traininglines = sourcelines[:training_len]
        target_traininglines = targetlines[:training_len]
        
        source_testlines = sourcelines[training_len+1:]
        target_testlines = targetlines[training_len+1:]
        for source_test_line, target_test_line in zip(source_testlines, target_testlines):
            test_line_valid = True
            for source_training_line, target_training_line in zip(source_traininglines, target_traininglines):
                if source_training_line == source_test_line or target_training_line == target_test_line:
                    test_line_valid = False
                    filtered_count += 1
                    break
            if test_line_valid:
                source_valid_test_lines.append(source_test_line)
                target_valid_test_lines.append(target_test_line)
            
        training_len = training_len - (len(source_valid_test_lines) - target_test_len +1)
        sys.stderr.write("Filtered {} sentences\n".format(filtered_count))
    
    sys.stderr.write("Writing training sentences\n")
    open(source_training_filename, 'w').write("\n".join(source_traininglines))
    open(target_training_filename, 'w').write("\n".join(target_traininglines))
    open(source_test_filename, 'w').write("\n".join(source_valid_test_lines))
    open(target_test_filename, 'w').write("\n".join(target_valid_test_lines))
