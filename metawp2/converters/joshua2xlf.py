"""
This program prints the best version of each sentence to a single file.
"""
import re
import os
#import time
import sys

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

    def __init__(self):
        self.lChildren = []
        
    def add_child(self, child):
        self.lChildren.append(child)

    def get_children(self):
        return self.lChildren

        
# -----------INPUT-----------
# file to be converted
FILENAME = sys.argv[1]

# input sentences
FILENAME_INPUT = sys.argv[2]

# source language
SOURCE_LANG = sys.argv[3]

# target language
TARGET_LANG = sys.argv[4]

# weights file
WEIGHTS_FILE = sys.argv[5]

# tool version
TOOL_VERSION = sys.argv[6] 

# t number
T_NUM = sys.argv[7]
# ---------INPUT END---------

f = open(FILENAME, 'r')
xlf = f.read().split('\n')
f.close()

g = open(FILENAME_INPUT, 'r')
INPUT_SNTS = g.read().split('\n')
g.close()

# Creates global string with name of output directory. 
DIR_NAME = ('t%s-%s-%s' % (T_NUM, SOURCE_LANG, TARGET_LANG))
#DIR_NAME = '%s_output' % (time.strftime('_%y%m%d_%H%M%S'))


# This method replaces tags with brackets back.
# It prevents confusing textual brackets and tree brackets.
def replace_brackets(string):
    return string.replace('<open>', '( ').replace('<close>', ' )')


# This method has an array of strings as input 
# and one string made of array items as an output.
def get_str(listVar):
    string = ''
    for item in listVar:
        string += item
    return string


# This method has as an input all translated sentences in nbest file. In this
# file the sentences are in descending order according to the translation word
# penalty. The method gets always the first (best) sentence and
# returns these as a list. 
def get_1best(xlf):
    bestSnts = []
    ids = set()
    for snt in xlf:
        # Number of sentence.
        snt_no = snt.partition(' ||| ')[0]
        # If a key 'snt_no' was already created in d.
        if snt_no not in ids:
            ids.add(snt_no)
            bestSnts.append( (snt, snt_no) )
    return bestSnts


# This method returns an annotation for a token. If the token is OOV, it sets
# the value on 1, otherwise 0. 
def annotate_OOV(token):
    if token.endswith('_OOV'):
        return '<annotation type=\"OOV\" value=\"1\" />'
    else :
        return '<annotation type=\"OOV\" value=\"0\" />'


# Removes a string '_OOV' from the end of a token, if the token has it.
def remove_OOV(string):
    return re.sub(r'([^ ]*)_OOV', r'\1', string)


# This method encapsulates each token to the appropriate tags.
def get_tokens_xml(string, s_phrase_id):
    tokens = string.split()
    output = '\n\t\t\t<tokens>'
    i = 1
    for token in tokens:
        s_token_id = '%s_k%s'% (s_phrase_id, str(i))
        output += '\n\t\t\t\t<token id=\"%s\">' % s_token_id
        output += '\n\t\t\t\t\t<string>%s</string>' % remove_OOV(token)
        output += '\n\t\t\t\t\t%s' % annotate_OOV(token)
        output += '\n\t\t\t\t</token>' 
        i += 1
    output += '\n\t\t\t</tokens>'
    return output


# This method gains information from an input sentence (=line in input file).
def get_sentence_attributes(line):
    # Returns a part beginning with '(ROOT{... ...)' and ending with '-#end#-'.
    s = '%s-#end#-' % (line.partition(' ||| ')[2].partition(' ||| ')[0])
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


# This method saves a "string node" (e.g. '[X]{9-12}'), creates a new node and
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


# This method gets and saves node attributes and a string, if exists. 
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
        node.sString += replace_brackets(sText)
        # sNodeString - Saves the gained string.
        # It is later used in the whole sentence composition.
        node.sNodeString += '<<>>%s' % (replace_brackets(sText))
    return node


# This method saves a string after node end, if the text exists. 
def operations_end_node(node, s, i):
    # sString --> between } and ) or between next to last ) and last ) 
    # - Gains a string in node, if exists.
    sText = replace_brackets(s[:i].rpartition('}')[2].split(')')[-1])
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


# This method composes the whole target language sentence and returns it.
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


# This method creates output format of a sentence in xml.
def create_output_file_content(node, line, snt_no):
    sXlf = ''
    sXlf += '\n<alt-trans tool-id="t%s" add:rank="1">' % (T_NUM)
    sXlf += '\n\t<source>%s</source>' % (INPUT_SNTS[line_no].strip())
    sXlf += '\n\t<target>%s</target>' % (remove_OOV(tarSnt))

    # total, lm, pt0, pt1, pt2
    scores = line.rpartition('|||')[0].rpartition('|||')[2].strip().split(' ')
    # word penalty
    if len(scores) == 5:
        scores.append(line.rpartition('|||')[2].strip())
        sXlf += '\n\t<add:scores>'
        sXlf += '\n\t\t<score type="total" value="%s" />' % (scores[5])
        sXlf += '\n\t\t<score type="lm" value="%s" />' % (scores[0])
        sXlf += '\n\t\t<score type="pt0" value="%s" />' % (scores[1])
        sXlf += '\n\t\t<score type="pt1" value="%s" />' % (scores[2])
        sXlf += '\n\t\t<score type="pt2" value="%s" />' % (scores[3])
        sXlf += '\n\t\t<score type="wordpenalty" value="%s" />' % (scores[4])
        sXlf += '\n\t</add:scores>'
    
        sXlf += '\n\t<add:derivation type="hiero_decoding" id="s%s_t1_r1_d1">'\
                % (snt_no)
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
                    sChildren += 's%s_p%s,' % (snt_no, str(child_no.iPhraseID))
                sChildren = '%s"' % (sChildren.strip(','))
    
            # Creates a phrase with node parameters
            # and with a node string, if exists.
            sPhrase_id = 's%s_t%s_r1_d1_p%s' % (snt_no, T_NUM,
                                                str(chList[0].iPhraseID))
            sXlf += '\n\t\t<phrase id=\"%s\" %s>' % (sPhrase_id, sChildren)
            if chList[0].sString:
                sXlf += get_tokens_xml(chList[0].sString.strip(), sPhrase_id)
            sXlf += '\n\t\t\t<annotation type="class" value="%s" />' % \
                    (chList[0].sClass)
            sXlf += '\n\t\t\t<alignment from="%s" to="%s" />' % \
                    (chList[0].iFrom, chList[0].iTo)
            sXlf += '\n\t\t</phrase>'
            
            # The processed (printed) node is removed from the list.
            chList.pop(0)
    
        sXlf += '\n\t</add:derivation>'
        sXlf += '\n</alt-trans>'
        
        return (sXlf.strip(), snt_no)


# This method creates xml files with transformed format of input sentences.
def create_xml_files():
    for (outputFileSnts, sntNumber) in XML_FILES:
        # Prints output format of sentences to .xml file.
        filenameSnts = '%s//t%s-%s-%s-%.4d.xml' % (DIR_NAME, T_NUM, \
                                     SOURCE_LANG, TARGET_LANG, long(sntNumber))
        f = open(filenameSnts, 'w')
        f.write(outputFileSnts)
        f.close()


# This method reads the input weights file and returns list of file lines.
def read_weight_file():
    a = open(WEIGHTS_FILE, 'r')
    content = a.readlines()
    a.close()
    return content


# This method receives lines of weight file and returns weights.
def get_weights(wFileContent):
    weights = []
    for line in wFileContent:
        weights.append(line.split(' ||| ')[1].strip())
    return weights


# This method receives weights and returns content for weights' output file.
def create_weights_output(weights):
    sWei = ''
    sWei += '<tool tool-id="t%s" tool-name="Joshua" tool-version=' \
            '"revision:%s">' % (T_NUM, TOOL_VERSION)
    sWei += '\n\t<add:weights>'
    sWei += '\n\t\t<weight type="lm" value="%s" />' % (weights[0])
    sWei += '\n\t\t<weight type="pt0" value="%s" />' % (weights[1])
    sWei += '\n\t\t<weight type="pt1" value="%s" />' % (weights[2])
    sWei += '\n\t\t<weight type="pt2" value="%s" />' % (weights[3])
    sWei += '\n\t\t<weight type="wordpenalty" value="%s" />' % (weights[4])
    sWei += '\n\t</add:weights>'
    sWei += '\n</tool>'
    return sWei


# This method prints weights to .xml file.
def write_weights_output_file(weightsOutput):
    filenameWeights = '%s//sysdesc-t%s-%s-%s.xml' % (DIR_NAME, T_NUM, \
                                                     SOURCE_LANG, TARGET_LANG)
    x = open(filenameWeights, 'w')
    x.write(weightsOutput)
    x.close()


# This method manages weights' creation.
def create_weights():
    wFileContent = read_weight_file()
    weights = get_weights(wFileContent)
    weightsOutput = create_weights_output(weights)
    write_weights_output_file(weightsOutput)


# Makes from XLF a list of best translated sentences.
xlf = get_1best(xlf)


#-------SELECT THE BEST SENTENCES-------
# This part of code selects the best sentence translation 
# from the list according to the reached word penalty.
#bestSnts = []
#d = {}
# Adds all sentences to dictionary d.
#for snt in xlf:
#    # Number of sentence.
#    snt_no = snt.partition(' ||| ')[0]
    # Reached word penalty.
#    snt_wp = snt.rpartition(' ||| ')[2]
    # If a key 'snt_no' was already created in d.
#    if snt_no in d:
        # Adds [word penalty, sentence] to a particular sentence number.
#        d[snt_no].append([snt_wp, snt])
#    else:
        # Creates a new key in d.
#        d[snt_no] = []
#        d[snt_no].append([snt_wp, snt])

#sntNumbers = d.keys()
# Selects the best sentence translation for each key in d.
#for sntNo in sntNumbers:
#    minWP = sys.maxint
#    snt = ''
#    for elem in d[sntNo]:
#        # If sentence translation word penalty is lower than so far reached.
#        if abs(float(elem[0])) < minWP:
            # Sets new minimal word penalty.
#            minWP = abs(float(elem[0]))
            # Sets new sentence translation with minimal word penalty.
#            snt = elem[1]
#    bestSnts.append(snt)
#-----END SELECT THE BEST SENTENCES-----


XML_FILES = []
line_no = 0
# This loop converts an input format of sentences into an output XLF format.
for (line, snt_no) in xlf:
    node = get_sentence_attributes(line)

    # Composes the whole sentence in target language.
    tarSnt = create_tar_lang_snt(node)

    # Creates content for output xml file.
    XML_FILES.append(create_output_file_content(node, line, snt_no))

    # Counts iterations in main for-loop.
    line_no += 1


# Creates a directory for output files.
os.mkdir(DIR_NAME)

# Creates xml files with transformed format of input sentences.
create_xml_files()

# Creates weights' xml file.
create_weights()
