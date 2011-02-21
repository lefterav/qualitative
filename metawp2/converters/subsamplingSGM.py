"""
This program reduces number of segments in both source and target SGM file
on a number required by user.
"""
import getopt
import re
import sys


class _Input:
    FILENAME_SOURCE = '' # name of source SGM file
    FILENAME_TARGET = '' # name of target SGM file
    SGM_2_KEEP = '' # number of segments to keep
    

# Function prints a list of all required and possible parameters.
def help():
    print "\nList of parameters:"
    print "-s [Source SGM file]"
    print "-t [Target SGM file]"
    print "-n [Number of segments to keep]\n"


# Function checks, if the user gave all required arguments.
def check_args(Input):
    stop = False
    if not Input.FILENAME_SOURCE:
        stop = True
        print "ERROR: Missing parameter --s [Source SGM file]"
    if not Input.FILENAME_TARGET:
        stop = True
        print "ERROR: Missing parameter -t [Target SGM file]"
    if not Input.SGM_2_KEEP:
        stop = True
        print "ERROR: Missing parameter -n [Number of segments to keep]"
    if stop:
        sys.exit("Program terminated.")


# Function reads the command line arguments, saves them to the Input class
# variables and checks, if the user gave all required arguments.
def read_commandline_args(Input):
    try:
        args = getopt.getopt(sys.argv[1:], "s:t:n:")[0]
    except getopt.GetoptError:
        help()
        sys.exit("Program terminated.")
        
    for opt, arg in args:
        if opt == '-s': Input.FILENAME_SOURCE = arg
        if opt == '-t': Input.FILENAME_TARGET = arg
        if opt == '-n': Input.SGM_2_KEEP = float(arg)
            
    check_args(Input)
    
    return Input

# This function returns a file content.
def get_file_content(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content


# This function checks, if number of segments in source and target contents are
# equal. It returns number of segments in each file (same for both files).
def get_total_seg_num(srcSegN, tgtSegN):
    if srcSegN != tgtSegN:
        print 'Number of source and target file segments is not equal!'
        sys.exit('Program terminated.')
    else:
        return srcSegN
    
    
# This function counts and returns an index for cutting the segments.
# The index determines how many segments should be kept (1 = 100 %).
def  get_cut_index(segN, seg2Keep):
    if segN < seg2Keep:
        sys.exit('\nNo. of segments to keep (%s) higher than no. of existing' \
                 ' segments (%s)!\n' % (int(seg2Keep), segN))
    return seg2Keep/segN


# This function counts and returns list of segment numbers for each 'doc'
# in a file (number of segments is equal both in source and target file)
# multiplied by cut index and rounded.
def get_seg_num_list(srcContent, cutIndex):
    segNumList = []
    for doc in srcContent.split('<doc docid=')[1:]:
        segNumList.append(int(round(doc.count('<seg id=')*cutIndex)))
    return segNumList


# This function returns a real number of segments that will be created.
def get_real_seg_num(sgmNumList):
    realSegN = 0
    for n in segNumList:
        realSegN+=n
    #print "Number of created segments: %s" % str(realSegN)
    return realSegN


# This function creates a new SGM file with required reduction of segments.
def create_new_SGM_file(oldContent, segNumList, oldFilename, realSegN):
    newContent = oldContent.partition('\n')[0]
    i = 0
    for doc in oldContent.split('<doc docid=')[1:]:
        core = re.split('<seg id="%s">' % segNumList[i], doc)[0]
        if core.count('<hl>') > core.count('</hl>'):
            core+= '</hl>\n'
            core = re.sub('<hl>\n</hl>\n', '', core)
        if core.count('<p>') > core.count('</p>'):
            core+= '</p>\n'
            core = re.sub('<p>\n</p>\n', '', core)
        newContent+= '\n<doc docid=%s</doc>' % (core)
        i+=1
    oldFilename = oldFilename.rpartition('.')[0]
    f = open('%s_%s.sgm' % (oldFilename, realSegN), 'w')
    f.write(newContent)
    f.close()
    print 'File %s_%s.sgm was created' % (oldFilename, realSegN)

    
#------------------------------------------------------------------------------
Input = _Input()
# Reads the command line input arguments. Explains what is the correct syntax
# in case of wrong input arguments and stops the program run.
Input = read_commandline_args(Input)

# Gets contents of source and target files.
srcContent = get_file_content(Input.FILENAME_SOURCE)
tgtContent = get_file_content(Input.FILENAME_TARGET)

# Gets total number of segments.
segN = get_total_seg_num(srcContent.count('<seg id='), \
                         tgtContent.count('<seg id='))

# Gets an index that sets how many segments should be kept (1.0 = 100 %).
cutIndex = get_cut_index(segN, Input.SGM_2_KEEP)

# Gets a list of numbers. Each number is a total amount of segments in 'doc'
# multiplied by cut index and rounded.
segNumList = get_seg_num_list(srcContent, cutIndex)

# Gets real number of created segments that may differ from required number.
realSegN = get_real_seg_num(segNumList)

# Creates a new SGM source file with required reduction of segments. 
create_new_SGM_file(srcContent, segNumList, Input.FILENAME_SOURCE, realSegN)

# Creates a new SGM target file with required reduction of segments. 
create_new_SGM_file(tgtContent, segNumList, Input.FILENAME_TARGET, realSegN)
