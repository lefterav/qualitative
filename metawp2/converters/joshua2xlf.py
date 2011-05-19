"""
This program prints the best version of each sentence to a single file.
"""
import getopt
import re
import os
import shutil
import sys


class _Input:
    FILENAME = '' # file with sentences in a tree format
    FILENAME_INPUT = '' # input sentences
    SOURCE_LANG = '' # source language
    TARGET_LANG = '' # target language
    WEIGHTS_FILE = '' # weights file
    TOOL_VERSION = '' # tool version 
    T_NUM = '' # t number
    INFO_FILE = '' # sentence info
    BEST_HYP = '' # number of best hypothesis per one sentence 


class _Node:
    sClass = ''
    parent = None
    iPhraseID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    sNodeString = ''
    sKey = ''
    nodeDict = dict()
    scores = [] 

    def __init__(self):
        self.lChildren = []
        
    def add_child(self, child):
        self.lChildren.append(child)

    def get_children(self):
        return self.lChildren
    

# Function prints a list of all required and possible parameters.
def help():
    print "\nList of parameters:"
    print "-c [File with sentences in a tree format]"
    print "-i [Input sentences]"
    print "-s [Source language]"
    print "-t [Target language]"
    print "(optional) -w [Weight file]"
    print "(optional) -v [Tool version]"
    print "(optional) -n [T-number]"
    print "(optional) -f [Sentence info file]"
    print "(optional) -h [Number of best hypothesis]\n"
    

# Function checks, if the user gave all required arguments.
def check_args(Input):
    stop = False
    if not Input.FILENAME:
        stop = True
        print "ERROR: Missing parameter -c [File with sentences in a tree " \
              "format]"
    if not Input.FILENAME_INPUT:
        stop = True
        print "ERROR: Missing parameter -i [File with sentences in source " \
              "language]"
    if not Input.SOURCE_LANG:
        stop = True
        print "ERROR: Missing parameter -s [Source language]"
    if not Input.TARGET_LANG:
        stop = True
        print "ERROR: Missing parameter -t [Target language]"
    if not Input.WEIGHTS_FILE:
        print "WARNING: Missing parameter -w [Weights file]"
    if not Input.TOOL_VERSION:
        print "WARNING: Missing parameter -v [Tool version]"
    if not Input.T_NUM:
        print "WARNING: Missing parameter -n [T-number]"
    if not Input.INFO_FILE:
        print "WARNING: Missing parameter -f [Sentence info file]"
    if not Input.BEST_HYP:
        print "WARNING: Missing parameter -h [Number of best hypothesis]"
        Input.BEST_HYP = 1
        print "Number of best hypothesis was set on 1."
    if stop:
        sys.exit("Program terminated.")


# Function reads the command line arguments, saves them to the Input class
# variables and checks, if the user gave all required arguments.
def read_commandline_args(Input):
    try:
        args = getopt.getopt(sys.argv[1:], "c:i:s:t:w:v:n:f:h:")[0]
    except getopt.GetoptError:
        help()
        sys.exit("Program terminated.")
        
    for opt, arg in args:
        if opt == '-c': Input.FILENAME = arg
        if opt == '-i': Input.FILENAME_INPUT = arg
        if opt == '-s': Input.SOURCE_LANG = arg
        if opt == '-t': Input.TARGET_LANG = arg
        if opt == '-w': Input.WEIGHTS_FILE = arg
        if opt == '-v': Input.TOOL_VERSION = arg
        if opt == '-n': Input.T_NUM = arg
        if opt == '-f': Input.INFO_FILE = arg
        if opt == '-h': Input.BEST_HYP = arg
            
    check_args(Input)
    
    return Input


# Function replaces tags with brackets back.
# It prevents confusing textual brackets and tree brackets.
def return_brackets(string):
    return string.replace('<open>', '( ').replace('<close>', ' )')


# Function has an array of strings as input 
# and one string made of array items as an output.
def get_str(listVar):
    string = ''
    for item in listVar:
        string += item
    return string


# Function parses an input info file. It returns a list of additional info 
# parameters for each sentence.
def getInfo():
    h = open(Input.INFO_FILE, 'r')
    content = h.read()
    h.close()
    info_strs = content.split('INFO: Sentence id=')[:-1]
    info = []
    for s in info_strs:
        info.append(re.match(r'ADDED: (\d+); MERGED: (\d+); PRUNED: (\d+); ' \
                             'PRE-PRUNED: (\d+), FUZZ1: (\d+), FUZZ2: (\d+); '\
                             'DOT-ITEMS ADDED: (\d+)', \
                             s.rpartition('INFO: ')[2]).groups())
    return info


# Function gains information from an input sentence (=line in input file).
def get_sentence_attributes(snt):
    # Returns a part beginning with '(ROOT{... ...)' and ending with '-#end#-'.
    s = '%s-#end#-' % (snt.partition(' ||| ')[2].partition(' ||| ')[0])
    # Replaces textual brackets with '<open>' and '<close>'.
    # It prevents confusing textual brackets and tree brackets.
    s = s.replace('( ', '<open>').replace(' )', '<close>')

    # A dictionary for "string nodes" (e. g. '[X]{12-21}')
    nodeDict = dict()
    # node initialisation
    node = _Node()
    # Number of phrase in input sentence.
    iPhraseID = 1
    # This loop has as many iterations as count of letters in string s.
    # String s is a input sentence.
    for i in range(len(s)):

        # If a root node starts (fulfilled only in 1. iteration).
        if re.findall('[(]ROO', s[i:i + 4]):
            node.iPhraseID = iPhraseID
            node = save_node_attributes(node, s, i)

        # If a next node starts (except root node), it creates new node and 
        # makes a connection (node.parent) with a previous one.
        if re.findall('[(][[].[]]', s[i:i + 4]):
            iPhraseID += 1
            node = create_new_node_and_connections(node, s, i, iPhraseID)
            node = save_node_attributes(node, s, i)

        # If a node ends.
        if s[i] == ')':
            node = operations_end_node(node, s, i)
            nodeDict[node.sKey] = [node.sNodeString]
            # If node.sClass is 'ROOT', keeps ROOT node as an actual node
            # in memory (important for printing part).
            if node.sClass != 'ROOT':
                # Parent node becomes (active) node.
                node = node.parent
    node.nodeDict = nodeDict
    return node


# Function saves a "string node" (e.g. '[X]{9-12}'), creates a new node and
# connections between new and old node (parent-child structure). 
def create_new_node_and_connections(node, s, i, index):
    # sNodeString - Saves each node in textual form (e. g. '[X]{3-7}').
    # It is later used in the whole sentence composition.
    node.sNodeString += '<<>>%s' % (re.search('[[].[]][{]\d+-\d+[}]', s[i:]) \
                                    .group(0))
    # Saves actual node to temp variable.
    oldnode = node
    # Creates new node.
    node = _Node()
    # Creates a connection between old node and his son.
    oldnode.add_child(node)
    # Creates a connection between new node and his father.
    node.parent = oldnode
    # Adds a number of phrase in input sentence.
    node.iPhraseID = index
    return node


# Function gets and saves node attributes and a string, if exists. 
def save_node_attributes(node, s, i):
    # sClass - Saves a node type (ROOT, S, X).
    node.sClass = re.search('[A-Z]+', s[i:i + 5]).group(0)
    # iFrom
    node.iFrom = re.match('.*?(\d+)-(\d+).*?', s[i:i + 14]).group(1)
    # iTo
    node.iTo = re.match('.*?(\d+)-(\d+).*?', s[i:i + 14]).group(2)
    # sString --> between } and ([ - Gains a string in node, if exists.
    sText = s[i:].partition('}')[2].partition(' ([')[0]
    if not sText.count(')') and sText:
        # sString - Saves the gained string.
        node.sString += return_brackets(sText)
        # sNodeString - Saves the gained string.
        # It is later used in the whole sentence composition.
        node.sNodeString += '<<>>%s' % (return_brackets(sText))
    return node


# Function saves a string after node end, if the text exists. 
def operations_end_node(node, s, i):
    # sString --> between } and ) or between next to last ) and last ) 
    # - Gains a string in node, if exists.
    sText = return_brackets(s[:i].rpartition('}')[2].split(')')[-1])
    # Gets scores for a node.
    try:
        node.scores = sText.split('<!-')[1].split('->')[0].strip('-') \
                      .split(',')
    except:
        #print "The sentence score was not found!"
        pass

    # Removes score tag from string. 
    sText = re.sub(' <!--([^>]*)>', '', sText)
    if sText:
        # sString - Saves the gained string.
        node.sString += sText
        # sNodeString - Saves the gained string.
        # It is later used in the whole sentence composition.
        node.sNodeString += '<<>>%s' % (sText)
    # sNodeString is splitted. The list may contain string(s)
    # or node(s) in textual form (e. g. [S]{0-3}).
    node.sNodeString = node.sNodeString.strip('<<>>').split('<<>>')
    # Creates a "string node". Example: '[X]{14-19}'  
    node.sKey = '[%s]{%s-%s}' % (node.sClass, str(node.iFrom), str(node.iTo))
    return node


# Function composes the whole target language sentence and returns it.
# Example of input variable:
# nodeStrings[16] == ['[X]{10-18}', ['kocham cie Kukuszu', '[X]{15-18}']]
def create_tar_lang_snt(node):
    # Gets all children (in format '[S]{0-3}') of ROOT node in a string.
    snt = get_str(node.sNodeString)

    i = 0
    # This part of code gets the whole sentence (target language).
    while re.findall('[[].[]][{]\d+-\d+[}]', snt) and i < 1000:
        for item in re.findall('[[].[]][{]\d+-\d+[}]', snt):
            snt = snt.replace(item, get_str(node.nodeDict[item][0]))
            break
        i += 1
    if i == 1000: print 'Error! Over 1000 iterations in creating sentence!'
    return snt.strip(' ')

# Function returns an annotation for a token. If the token is OOV, it sets
# the value on 1, otherwise 0. 
def annotate_OOV(token):
    if token.endswith('_OOV'):
        return '<metanet:annotation type=\"OOV\" value=\"1\" />'
    else :
        return '<metanet:annotation type=\"OOV\" value=\"0\" />'


# Removes a string '_OOV' from the end of a token, if the token has it.
def remove_OOV(string):
    return re.sub(r'([^ ]*)_OOV', r'\1', string)


# Function encapsulates each token to the appropriate tags.
def get_tokens_xml(string, s_phrase_id, scores):
    tokens = string.split()
    output = '\n\t\t\t<metanet:tokens>'
    i = 1
    for token in tokens:
        s_token_id = '%s_k%s'% (s_phrase_id, str(i))
        output += '\n\t\t\t\t<metanet:token id=\"%s\">' % s_token_id
        output += '\n\t\t\t\t\t<metanet:string>%s</metanet:string>' % \
                  remove_OOV(token)
        output += get_scores_xml(scores)
        output += '\n\t\t\t\t\t%s' % annotate_OOV(token)
        output += '\n\t\t\t\t</metanet:token>' 
        i += 1
    output += '\n\t\t\t</metanet:tokens>'
    return output


# Function creates output format for node scores. An input is the whole tag
# with scores, e. g. ' <!---3.561,17.192,0.000,0.000,0.000,0.000-->'. 
def get_scores_xml(scores):
    output = ''
    final_output = ''
    i = 0
    for score in scores:
        output += '\n\t\t\t\t\t\t<metanet:score type="translogp%d">%s' \
                  '</metanet:score>' % (i, score)
        i += 1
    if output != '' :
        final_output = '\n\t\t\t\t\t<metanet:scores>%s\n\t\t\t\t\t' \
                       '</metanet:scores>' % output
    return final_output


# Function creates output format of a sentence in xml.
def create_output_file_content(node, snt, snt_no, rank):
    sXlf = ''
    sXlf += '\n<alt-trans tool-id="t%s" metanet:rank="%s">' % (Input.T_NUM, \
                                                               rank)
    sXlf += '\n\t<source xml:lang="%s">%s</source>' % (Input.SOURCE_LANG, \
                                                   INPUT_SNTS[snt_no].strip())
    sXlf += '\n\t<target xml:lang="%s">%s</target>' % (Input.TARGET_LANG, \
                                                       remove_OOV(tarSnt))

    # total, lm, pt0, pt1, pt2
    scores = snt.rpartition('|||')[0].rpartition('|||')[2].strip().split(' ')
    # word penalty
    if len(scores) == 5:
        scores.append(snt.rpartition('|||')[2].strip())
        sXlf += '\n\t<metanet:scores>'
        sXlf += '\n\t\t<metanet:score type="total" value="%s" />' % (scores[5])
        sXlf += '\n\t\t<metanet:score type="lm" value="%s" />' % (scores[0])
        sXlf += '\n\t\t<metanet:score type="pt0" value="%s" />' % (scores[1])
        sXlf += '\n\t\t<metanet:score type="pt1" value="%s" />' % (scores[2])
        sXlf += '\n\t\t<metanet:score type="pt2" value="%s" />' % (scores[3])
        sXlf += '\n\t\t<metanet:score type="wordpenalty" value="%s" />' % \
                (scores[4])
        sXlf += '\n\t</metanet:scores>'
        
        if Input.INFO_FILE:
            sXlf += '\n\t<metanet:derivation type="hiero_decoding" id="' \
                    's%s_t1_d1">' % (snt_no)
            sXlf += '\n\t<metanet:annotation type="added" value="%s" />' % \
                    I_NUMS[snt_no][0]
            sXlf += '\n\t<metanet:annotation type="merged" value="%s" />' % \
                    I_NUMS[snt_no][1]
            sXlf += '\n\t<metanet:annotation type="pruned" value="%s" />' % \
                    I_NUMS[snt_no][2]
            sXlf += '\n\t<metanet:annotation type="pre-pruned" value="%s" />'%\
                    I_NUMS[snt_no][3]
            sXlf += '\n\t<metanet:annotation type="fuzz1" value="%s" />' % \
                    I_NUMS[snt_no][4]
            sXlf += '\n\t<metanet:annotation type="fuzz2" value="%s" />' % \
                    I_NUMS[snt_no][5]
            sXlf += '\n\t<metanet:annotation type="dot-items added" ' \
                    'value="%s" />' % I_NUMS[snt_no][6]
        chList = [node]
        while chList:
            i = 1
            # This loop adds all children of a node chList[0]
            # between chList[0] and chList[2].
            for child in chList[0].get_children():
                chList.insert(i, child)
                i += 1
    
            # Creates a string with a list of children.
            sChildren = ''
            if len(chList[0].get_children()):
                sChildren = ' children="'
                for child_no in chList[0].get_children():
                    sChildren += 's%s_t%s_r%s_d1_p%s,' % (snt_no, \
                                    Input.T_NUM, rank, str(child_no.iPhraseID))
                sChildren = '%s"' % (sChildren.strip(','))
    
            # Creates a phrase with node parameters
            # and with a node string, if exists.
            sPhrase_id = 's%s_t%s_r%s_d1_p%s' % (snt_no, Input.T_NUM, \
                                                rank, str(chList[0].iPhraseID))
            sXlf += '\n\t\t<metanet:phrase id=\"%s\" %s>' % \
                    (sPhrase_id, sChildren)
            if chList[0].sString:
                sXlf += get_tokens_xml(chList[0].sString.strip(), sPhrase_id, \
                                       chList[0].scores)
            sXlf += '\n\t\t\t<metanet:annotation type="class" value="%s" />' %\
                    (chList[0].sClass)
            sXlf += '\n\t\t\t<metanet:alignment from="%s" to="%s" />' % \
                    (chList[0].iFrom, chList[0].iTo)
            sXlf += '\n\t\t</metanet:phrase>'
            
            # The processed (printed) node is removed from the list.
            chList.pop(0)
    
        sXlf += '\n\t</metanet:derivation>'

        sXlf += '\n</alt-trans>'
        
        return (sXlf.strip(), snt_no, rank)


# Function creates xml files with transformed format of input sentences.
def create_xlf_files():
    for (outputFileSnts, snt_no, rank) in XLF_FILES:
        # Prints output format of sentences to .xml file.
        filenameSnts = '%s//t%s-%s-%s-s%.4d-r%.4d.xml' % (DIR_NAME, \
                       Input.T_NUM, Input.SOURCE_LANG, Input.TARGET_LANG, \
                       long(snt_no), long(rank))
        f = open(filenameSnts, 'w')
        f.write(outputFileSnts)
        f.close()


# Function reads the input weights file and returns list of file lines.
def read_weight_file():
    a = open(Input.WEIGHTS_FILE, 'r')
    content = a.readlines()
    a.close()
    return content


# Function receives lines of weight file and returns weights.
def get_weights(wFileContent):
    weights = []
    for line in wFileContent:
        weights.append(line.split(' ||| ')[1].strip())
    return weights


# Function receives weights and returns content for weights' output file.
def create_weights_output(weights):
    sWei = ''
    sWei += '<tool tool-id="t%s" tool-name="Joshua" tool-version=' \
            '"revision:%s">' % (Input.T_NUM, Input.TOOL_VERSION)
    sWei += '\n\t<metanet:weights>'
    sWei += '\n\t\t<metanet:weight type="lm" value="%s" />' % (weights[0])
    sWei += '\n\t\t<metanet:weight type="pt0" value="%s" />' % (weights[1])
    sWei += '\n\t\t<metanet:weight type="pt1" value="%s" />' % (weights[2])
    sWei += '\n\t\t<metanet:weight type="pt2" value="%s" />' % (weights[3])
    sWei += '\n\t\t<metanet:weight type="wordpenalty" value="%s" />' % \
            (weights[4])
    sWei += '\n\t</metanet:weights>'
    sWei += '\n</tool>'
    return sWei


# Function prints weights to .xml file.
def write_weights_output_file(weightsOutput):
    filenameWeights = '%s//sysdesc-t%s-%s-%s.xml' % (DIR_NAME, Input.T_NUM, \
                                                     Input.SOURCE_LANG, \
                                                     Input.TARGET_LANG)
    x = open(filenameWeights, 'w')
    x.write(weightsOutput)
    x.close()


# Function manages weights' creation.
def create_weights():
    wFileContent = read_weight_file()
    weights = get_weights(wFileContent)
    weightsOutput = create_weights_output(weights)
    write_weights_output_file(weightsOutput)


Input = _Input()
# Reads the command line input arguments. Explains what is the correct syntax
# in case of wrong input arguments and stops the program run.
Input = read_commandline_args(Input)

# Opens file with source language sentences and saves it's content.
g = open(Input.FILENAME_INPUT, 'r')
INPUT_SNTS = g.read().strip().split('\n')
g.close()

# Gets info about sentences from the sentence info file.
if Input.INFO_FILE:
    I_NUMS = getInfo()

# Opens file with sentences in a tree format and saves it's content.
f = open(Input.FILENAME, 'r')
content = f.read().split('\n')
f.close()

XLF_FILES = []
old_snt_no = -1
# This loop converts an input format of sentences into an output XLF format.
for snt in content:
    
    # Gets a sentence number.
    try:
        snt_no = int(re.match(r"(\d+)", snt).group(1))
    except:
        continue
    # Sets rank to 1 in case of new sentence.
    if snt_no > old_snt_no:
        rank = 1
    # Jumps to next iteration in case of higher rank than required. 
    if int(Input.BEST_HYP) < rank:
        continue

    # Saves the sentence information to a class node.
    node = get_sentence_attributes(snt)

    # Composes the whole sentence in target language.
    tarSnt = create_tar_lang_snt(node)

    # Creates content for output XLF file.
    output_file_content = create_output_file_content(node, snt, snt_no, rank)
    if (output_file_content):
        XLF_FILES.append(output_file_content)

    # Raises a hypothesis rank by 1.
    rank += 1
    # Saves old number of sentence.
    old_snt_no = snt_no

# Creates a directory for output files. 
DIR_NAME = ('t%s-%s-%s' % (Input.T_NUM, Input.SOURCE_LANG, Input.TARGET_LANG))
if os.path.exists(DIR_NAME):
    shutil.rmtree(DIR_NAME)
os.mkdir(DIR_NAME) 

# Creates files with XLF format from input sentences in tree format.
create_xlf_files()

# Creates weights' XLF file, if input weights file is available.
if Input.WEIGHTS_FILE:
    create_weights()
