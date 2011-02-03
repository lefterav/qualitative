'''
This module reads targets of Joshua output xlf files and saves those targets
one per a line in a new file. The only parameter of this file is the address
of Joshua output directory.
'''
import os
import sys
# This is an input parameter - location of Joshua output directory.
JOSHUA_OUTPUT_DIR_ADDR = sys.argv[1]

JOSHUA_OUTPUT_DIR = JOSHUA_OUTPUT_DIR_ADDR.strip('/').rpartition('/')[2] 

# This set contains parts of filenames in Joshua output directory. Files 
# containing these string shouldn't be processed.
UNDESIRED_FILENAMES = set(['sysdesc','targets'])


# This method gets a list of files in Joshua output directory, returns a set of
# undesired files.
def get_undesired_filenames(JFiles): 
    undesiredFiles = []
    for filename in JFiles:
        for xfilename in UNDESIRED_FILENAMES: 
            if filename.count(xfilename) and filename.count(JOSHUA_OUTPUT_DIR):
                undesiredFiles.append(filename)
                break
    return undesiredFiles


# This method returns a list of filenames in Joshua output directory. 
def get_filenames():
    try:
        JFiles = os.listdir(JOSHUA_OUTPUT_DIR_ADDR)
    except:
        print "Error dir address! Can't find the Joshua output directory!"
    return JFiles


# This method receives a list of filenames and a list of undesired filenames
# in Joshua output directory. It returns only filenames to be processed. 
def get_target_strings(files, undesiredFiles):
    targetStrings = []
    for filename in files:
        if filename not in undesiredFiles:
            f = open('%s/%s' % (JOSHUA_OUTPUT_DIR_ADDR, filename), 'r')
            target = f.read().partition('<target>')[2] \
                             .partition('</target>')[0].strip()
            f.close()
            targetStrings.append(target)
    return targetStrings


# This method prints the target strings (sentences) to the output file.
def print_targets(targetStrings):
    filename = '%s/targets-%s.txt' % (JOSHUA_OUTPUT_DIR_ADDR, \
                                      JOSHUA_OUTPUT_DIR)
    output = ''
    for targetStr in targetStrings: 
        output += '%s\n' % (targetStr)
    
    f = file(filename, 'w')
    f.write(output.strip())
    f.close()
    print 'Targets were successfully written to %s' % (filename)


# Gets filenames from the Joshua output directory.
files = get_filenames()

# Gains undesired filenames from the Joshua output directory.
undesiredFiles = get_undesired_filenames(files)

# Parses target strings from the Joshua output files.
targetStrings = get_target_strings(files, undesiredFiles)

# Prints targets to a special file into the Joshua output directory.
print_targets(targetStrings)


