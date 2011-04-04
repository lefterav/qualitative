"""
Description: Converts data in EuroScript's format in plain text and vice versa
Author: Eleftherios Avramidis
"""
import getopt
import re
import sys


class _Input:
    """Stores information about the input."""
    SOURCE_FILENAME = None # source filename
    TARGET_SENTENCES_FILENAME = None # filename of target
    # sentences list
    SOURCE_SENTENCES_FILENAME = '' # required filename
    OUTPUT_FILENAME = None
    # of source sentences list
    SYSTEM = '' # system (z.B. Google)
    TARGET_LANG = '' # target language


def usage():
    """Prints a list of all required and possible parameters."""
    print "\nList of parameters:" \
    "-i [Input filename in DEB format]" \
    "-t [Output filename for sentence/line extraction  (function 1)]" \
    "-j [Input filename containing translated sentences in " \
      "sentence/line format]" \
    "-o [Output filename re-wrapping translation outcome into the original " \
      " format (function 2)]" \
    "-s [Name/id of system]" \
    "-l [Target language code e.g. en]\n"


def check_args(_input):
    """Checks user provided arguments for completeness."""
    stop = False
    if not _input.SOURCE_FILENAME:
        stop = True
        print "ERROR: Missing parameter -i [Input filename]"
#    if not _input.SOURCE_SENTENCES_FILENAME:
#        stop = True
#        print "ERROR: Missing parameter -t [Required name of output " \
#          "file with source sentences list]"
#    if not _input.TARGET_SENTENCES_FILENAME:
#        stop = True    
#        print "ERROR: Missing parameter -j [Name of input file " \
#          "with target sentences list]"
#    if not _input.SYSTEM:
#        stop = True
#        print "ERROR: Missing parameter -s [Kind of system format]"
#    if not _input.TARGET_LANG:
#        stop = True
#        print "ERROR: Missing parameter -l [Target language]"
    if stop:
        sys.exit("Program terminated.")


def read_commandline_args(_input):
    """Reads arguments, creates Input objects and checks them."""
    try:
        args = getopt.getopt(sys.argv[1:], "i:j:t:o:s:l:")[0]
    
    except getopt.GetoptError:
        usage()
        sys.exit("Program terminated.")
    
    for opt, arg in args:
        if opt == '-i':
            _input.SOURCE_FILENAME = arg
        
        if opt == '-j':
            _input.TARGET_SENTENCES_FILENAME = arg
        
        if opt == '-t':
            _input.SOURCE_SENTENCES_FILENAME = arg
        
        if opt == '-o':
            _input.OUTPUT_FILENAME = arg
        
        if opt == '-s':
            _input.SYSTEM = arg
        
        if opt == '-l':
            _input.TARGET_LANG = arg
    
    check_args(_input)
    return _input


def read_source_file(filename):
    """Reads the file and returns its content."""
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content


def save_source_sentences(filename, text):
    """Saves source sentences line by line as a list to the file."""
    f = open(filename, 'w')
    for sentence in text.split('<source>')[1:]:
        f.write('%s\n' % (sentence.split('</source>')[0]))
    f.close()


def read_target_sentences(filename):
    """Reads the target sentences from the file."""
    f = open(filename, 'r')
    trg_sentences = f.read().strip().split('\n')
    f.close()
    return trg_sentences


def compare_snt_counts(text, trg_sentences):
    """Compares count of source and target sentences."""
    if text.count('<source>') > len(trg_sentences):
        print 'ERROR: Less target sentences than source sentences!'
        sys.exit("Program terminated.")
    
    elif text.count('<source>') < len(trg_sentences):
        print 'WARNING: Less source sentences than target sentences!'


# This function replaces the source sentences with the target sentences
# and adds sysid parameter to the beginning tag.
def replace_src_with_trg(text, system, target_lang, trg_sentences):
    """Replaces source with target sentences and adds sysid to the tags."""
    i = 0
    for sentence in text.split('<source>')[1:]:
        ###
        ### Use str.format(...) instead of str % (...) !
        ###
        replaced = re.sub('[^<]*</source>', '%s</target>' % \
                  trg_sentences[i], sentence)
        text = text.replace(sentence, replaced)
        i += 1
    
    text = text.replace('<source>', '<target system="%s">' % (system))
    text = text.partition(' ')[0] + ' sysid="%s" ' % \
           (system) + text.partition(' ')[2]
    text = '<tstset trglang="%s">\n%s\n</tstset>' % (target_lang, text)
    return text


def create_output_file(filename, output_filename, text):
    """Creates an output file with target sentences and modifications."""
#    output_filename = '%s_output.%s' % (filename.rpartition('.')[0], \
#                        filename.rpartition('.')[2])
    g = open(output_filename, 'w')
    g.write(text)
    g.close()
    print 'The file %s was converted to %s.' % (filename, output_filename)



###
### Create a "main()" method which does that...
### Encapsulate thise method in an 'if __name__ == "__main__":' block.
###

# Reads the command line input arguments. Explains what is the correct syntax
# in case of wrong input arguments and stops the program run.
INPUT = _Input()
INPUT = read_commandline_args(INPUT)

###
### Why don't you create the _Input instance INSIDE the read_commandline_args
### method instead???
###

if (INPUT.SOURCE_FILENAME and INPUT.SOURCE_SENTENCES_FILENAME != ''):
    # Reads the source file.
    TEXT = read_source_file(INPUT.SOURCE_FILENAME)
    
    # Saves source sentences line by line as a list to the file.
    save_source_sentences(INPUT.SOURCE_SENTENCES_FILENAME, TEXT)
    print 

else:
    # Reads the source file.
    TEXT = read_source_file(INPUT.SOURCE_FILENAME)
    
    # Reads the target sentences from the file.
    TRG_SENTENCES = read_target_sentences(INPUT.TARGET_SENTENCES_FILENAME)
    
    # Compares count of source and target sentences.
    compare_snt_counts(TEXT, TRG_SENTENCES)
    
    # Replaces the source sentences with the target sentences and adds
    # sysid parameter to the beginning tag.
    TEXT = replace_src_with_trg(TEXT, INPUT.SYSTEM, INPUT.TARGET_LANG,
      TRG_SENTENCES)
    
    # Creates an output file with target sentences and above made modifications.
    create_output_file(INPUT.SOURCE_FILENAME, INPUT.OUTPUT_FILENAME, TEXT)

