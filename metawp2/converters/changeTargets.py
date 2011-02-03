'''
This module creates new Joshua output XLF files to the directory named
changed_targets. These new files have new target sentences according to the
target sentence file.
'''
import re
import os
import sys


# This is an input parameter - location of Joshua output directory.
JOSHUA_OUTPUT_DIR_ADDR = sys.argv[1]

# This is an input parameter - location of a file with targets sentences.
TARGET_SENTENCE_FILE = sys.argv[2]

JOSHUA_OUTPUT_DIR = JOSHUA_OUTPUT_DIR_ADDR.strip('/').rpartition('/')[2]

CHANGED_TARGETS_DIR_ADDR = JOSHUA_OUTPUT_DIR_ADDR.strip('/').rpartition('/')[0]

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
        print "Error dir address! Can't find the Joshua output directory!\n"
        return -1
    return JFiles


# This method reads target sentence file in Joshua output directory and
# returns a list of target sentences.
def read_target_sentence_file():
    targets = []
    f = open('/%s' % (TARGET_SENTENCE_FILE), 'r')
    for line in f:
        if not line.isspace():
            targets.append(line.strip())
    f.close()
    return targets
        

# This method replaces old targets in the directory changed_targets for new
# targets. Those new targets were gained from target sentence file by script
# 'getTargets.py'. 
def replace_targets(target, content):
    str2replace = re.findall('<target>.*</target>', content)[0]
    return content.replace(str2replace, '<target>%s</target>' % (target))


# This method creates a new directory and creates there Joshua output files 
# with new target sentences.
def create_files(filenames, undesiredFiles, targets):
    dirPath = '/%s/%s_changed_targets' % (CHANGED_TARGETS_DIR_ADDR, \
                                          JOSHUA_OUTPUT_DIR)
    if os.path.exists(dirPath):
        print 'The directory "changed_targets already exists!\n'
        return -1
    else:
        os.mkdir(dirPath)
        
    i = 0
    for filename in filenames:
        if filename not in undesiredFiles and filename.endswith('.xml'):
            # Reads old Joshua output files.
            f = open('%s/%s' % (JOSHUA_OUTPUT_DIR_ADDR, filename), 'r')
            content = f.read()
            f.close()
            
            # Replaces old targets for new ones.
            newContent = replace_targets(targets[i], content)
            g = open('/%s/%s_changed_targets/%s' % (CHANGED_TARGETS_DIR_ADDR, \
                                             JOSHUA_OUTPUT_DIR, filename), 'w')
            g.write(newContent)
            g.close()
            i += 1
    if i == len(targets):
        print 'XLF files successfully copied and replaced by new targets!\n'
        return 0
    elif i < len(targets):
        print 'More target files than XLF files or some XLF files missing!'
        print 'Results in "changed_targets" directory may not be completed!\n'
        return -1
    
#----------------------------------MAIN----------------------------------------
# Gets filenames from the Joshua output directory.
filenames = get_filenames()

# Gains undesired filenames from the Joshua output directory.
undesiredFiles = get_undesired_filenames(filenames)

# Reads target sentence file and returns list of target sentences.
targets = read_target_sentence_file()

# Creates a new directory and creates there Joshua output XLF files with new 
# targets sentences.
create_files(filenames, undesiredFiles, targets)
