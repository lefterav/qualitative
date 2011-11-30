'''
Created on 29 Nov 2011

@author: elav01
'''
import sys
import re

def process_file(filename, lineindexfile_out, threshold, min_id = 39770, max_id = 42877, regfilters = []):
    
    ''' 
    Provide a list with the line indexes of the source sentences that have a length higher than the threshold
    '''
    
    file = open(filename, 'r')
    indexfile = open(lineindexfile_out, 'w')
    lines = []
    threshold = int(threshold)
    min_id = int(min_id)
    max_id = int(max_id)
    i = 0
    for line in file:
        i += 1
        tokens = line.split()
        length = len(tokens)
        if length >= threshold and not filterstring(line, regfilters) and i > min_id and i < max_id:
            lines.append(i)
            indexfile.write("%s\n" % str(i))
            
    file.close()
    indexfile.close()
    return lines
         
def filterstring(string, regexclude):
    '''
    If any of the regular expressions provided (filter) matches this string, return True
    '''
    for regexp in regexclude:
        if re.search(regexp, string):
            print "filtered sentence"
            return True
            
    

def filter_sentences(filename_in, filename_out, lineindexes):
    '''
    Select the sentences that correspond to the given line index 
    '''
    
    file_in = open(filename_in, 'r')
    file_out = open(filename_out, 'w')
    i = 0
    for line in file_in:
        i += 1
        if i in lineindexes:
            file_out.write(line)
            
    file_in.close()
    file_out.close()

def read_lineindexes_from_file(lineindexfile_in):
    file_in = open(lineindexfile_in, 'r')
    lineindexes = [int(line.strip()) for line in file_in  ]
    return lineindexes

if __name__ == '__main__':
    argument_length = len(sys.argv[1:])
    
    if argument_length == 2:
        (filename_src_in, lineindexfile_out) = sys.argv[1:]
        lineindexes = process_file(filename_src_in, lineindexfile_out)
        print "Got line indexes for %d sentences which I wrote to the specified file" % len(lineindexes)
        
    if argument_length > 5:
        (filename_src_in, lineindexfile_out, threshold, min_id, max_id) = sys.argv[1:6]
        regexclude = sys.argv[6:]
        lineindexes = process_file(filename_src_in, lineindexfile_out, threshold, min_id, max_id, regexclude)
        print "Got line indexes for %d sentences which I wrote to the specified file" % len(lineindexes)
        
    elif argument_length == 5:
        (filename_src_in, filename_src_out, filename_tgt_in, filename_tgt_out, lineindexfile_out) = sys.argv[1:]
        lineindexes = process_file(filename_src_in, lineindexfile_out)
        print "Got line indexes for %d sentences" % len(lineindexes)
        filter_sentences(filename_src_in, filename_src_out, lineindexes)
        print "Filtered source file"
        filter_sentences(filename_tgt_in, filename_tgt_out, lineindexes)
        print "Filtered target file"
        
    elif argument_length == 3:
        (filename_in, filename_out, lineindexfile_in) = sys.argv[1:]
        if filename_in == filename_out:
            print "You have given the same name for in and out. Please check or your input will be overwritten"
        else:
            lineindexes = read_lineindexes_from_file(lineindexfile_in)
            print "Got line indexes for %d sentences" % len(lineindexes)
            filter_sentences(filename_in, filename_out, lineindexes)

    else:
        print "Examples:"
        print "python cs-en_tgt.txt selected_ids.txt 4 39770 42877 \"\" \n"
        print "\tExtract all sentences with more than 4 words with numerical ID between 39770 and 42877 and no string filtering"
        print "\tThen you have to use the produced links file, in order to filter one file at a time"
        
        
    
    