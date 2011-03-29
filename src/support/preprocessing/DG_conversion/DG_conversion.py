import getopt
import re
import sys


class _Input:
    SOURCE_FILENAME = '' # source filename
    TARGET_SENTENCES_FILENAME = '' # filename of target
    # sentences list
    SOURCE_SENTENCES_FILENAME = '' # required filename
    OUTPUT_FILENAME = ''
    # of source sentences list
    SYSTEM = '' # system (z.B. Google)
    TARGET_LANG = '' # target language


# Function prints a list of all required and possible parameters.
def help():
    print "\nList of parameters:"
    print "-i [Input filename]"
    print "-o [Output filename]"
    print "-j [Name of input file with target sentences list]"
    print "-t [Required name of output file with source sentences list]"
    print "-s [Kind of system]"
    print "-l [Target language]\n"
    

# Function checks, if the user gave all required arguments.
def check_args(Input):
    stop = False
    if not Input.SOURCE_FILENAME:
        stop = True
        print "ERROR: Missing parameter -i [Input filename]"
#    if not Input.SOURCE_SENTENCES_FILENAME:
#        stop = True
#        print "ERROR: Missing parameter -t [Required name of output " \
#          "file with source sentences list]"
#    if not Input.TARGET_SENTENCES_FILENAME:
#        stop = True
#        print "ERROR: Missing parameter -j [Name of input file " \
#          "with target sentences list]"
#    if not Input.SYSTEM:
#        stop = True
#        print "ERROR: Missing parameter -s [Kind of system format]"
#    if not Input.TARGET_LANG:
#        stop = True
#        print "ERROR: Missing parameter -l [Target language]"
    if stop:
        sys.exit("Program terminated.")


# Function reads the command line arguments, saves them to the Input class
# variables and checks, if the user gave all required arguments.
def read_commandline_args(Input):
    try:
        args = getopt.getopt(sys.argv[1:], "i:j:t:s:l:")[0]
    except getopt.GetoptError:
        help()
        sys.exit("Program terminated.")
        
    for opt, arg in args:
        if opt == '-i': Input.SOURCE_FILENAME = arg
        if opt == '-j': Input.TARGET_SENTENCES_FILENAME = arg
        if opt == '-t': Input.SOURCE_SENTENCES_FILENAME = arg
        if opt == '-o': Input.OUTPUT_FILENAME = arg
        if opt == '-s': Input.SYSTEM = arg
        if opt == '-l': Input.TARGET_LANG = arg
            
    check_args(Input)
    
    return Input


# This function reads the file and returns its content.
def read_source_file(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content


# This function saves source sentences line by line as a list to the file.
def save_source_sentences(filename, text):
    f = open(filename, 'w')
    for sentence in text.split('<source>')[1:]:
        f.write('%s\n' % (sentence.split('</source>')[0]))
    f.close()


# This function reads the target sentences from the file.
def read_target_sentences(filename):
    f = open(filename, 'r')
    trg_sentences = f.read().strip().split('\n')
    f.close()
    return trg_sentences


# This function compares count of source and target sentences.
def compare_snt_counts(text, trg_sentences):
    if text.count('<source>') > len(trg_sentences):
        print 'ERROR: Less target sentences than source sentences!'
        sys.exit("Program terminated.")
    elif text.count('<source>') < len(trg_sentences):
        print 'WARNING: Less source sentences than target sentences!'


# This function replaces the source sentences with the target sentences
# and adds sysid parameter to the beginning tag.
def replace_src_with_trg(text, system, target_lang, trg_sentences):
    i = 0
    for sentence in text.split('<source>')[1:]:
        replaced = re.sub('[^<]*</source>', '%s</target>' % \
                  trg_sentences[i], sentence)
        text = text.replace(sentence, replaced)
        i += 1
    text = text.replace('<source>', '<target system="%s">' % (system))
    text = text.partition(' ')[0] + ' sysid="%s" ' % \
           (system) + text.partition(' ')[2]
    text = '<tstset trglang="%s">\n%s\n</tstset>' % (target_lang, text)
    return text


# This function creates file with target sentences and modifications.
def create_output_file(filename, output_filename, text):
#    output_filename = '%s_output.%s' % (filename.rpartition('.')[0], \
#                        filename.rpartition('.')[2])
    g = open(output_filename, 'w')
    g.write(text)
    g.close()
    print 'The file %s was converted to %s.' % (filename, output_filename)



# Reads the command line input arguments. Explains what is the correct syntax
# in case of wrong input arguments and stops the program run.
Input = _Input()
Input = read_commandline_args(Input)

if (Input.SOURCE_FILENAME and Input.SOURCE_SENTENCES_FILENAME):
    # Reads the source file.
    text = read_source_file(Input.SOURCE_FILENAME)
    
    # Saves source sentences line by line as a list to the file.
    save_source_sentences(Input.SOURCE_SENTENCES_FILENAME, text)
    
else:
    # Reads the source file.
    text = read_source_file(Input.SOURCE_FILENAME)
    
    # Reads the target sentences from the file.
    trg_sentences = read_target_sentences(Input.TARGET_SENTENCES_FILENAME)
    
    # Compares count of source and target sentences.
    compare_snt_counts(text, trg_sentences)
    
    # Replaces the source sentences with the target sentences and adds
    # sysid parameter to the beginning tag.
    text = replace_src_with_trg(text, Input.SYSTEM, Input.TARGET_LANG, trg_sentences)
    
    # Creates an output file with target sentences and above made modifications.
    create_output_file(Input.SOURCE_FILENAME, Input.OUTPUT_FILENAME, text)

