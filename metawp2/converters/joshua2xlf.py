"""
This program prints the best version of each sentence to a single file.
"""
import re
import os
import time
import sys

class _Node:
    sClass = ''
    parent = None
    iPhraseID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    sNodeString = ''

    def __init__(self):
        self.lChildren = []
        
    def add_child(self, child):
        self.lChildren.append(child)

    def get_children(self):
        return self.lChildren
        
# This method replaces tags with brackets back.
# It prevents confusing textual brackets and tree brackets.
def replace_brackets(string):
    return string.replace('<open>', '( ').replace('<close>', ' )')

# This method has an array of strings as input 
# and one string made of array items as an output.
def get_str(listVar):
    string = ''
    for item in listVar:
        string = string + item
    return string


def get_1best (xlf):
    bestSnts = []
    d={}
    ids = set()
    for snt in xlf:
        # Number of sentence.
        snt_no = snt.partition(' ||| ')[0]
        # If a key 'snt_no' was already created in d.
        if snt_no not in ids:
            ids.add(snt_no)
            bestSnts.append( (snt, snt_no) )
            
            
    return bestSnts

def annotate_OOV (token):
    if token.endswith("_OOV"):
        return "<annotation type=\"OOV\" value=\"1\" />"
    else :
        return "<annotation type=\"OOV\" value=\"0\" />"

def remove_OOV (string):
    return re.sub(r'([^ ]*)_OOV', r'\1', string)

def get_tokens_xml (string, s_phrase_id):
    tokens = string.split()
    output = "\n\t\t\t<tokens>"
    i = 1
    for token in tokens:
        s_token_id = "%s_k%s"% (s_phrase_id, str(i))
        output += "\n\t\t\t\t<token id=\"%s\">" %s_token_id
        output += "\n\t\t\t\t\t<string>%s</string>" %remove_OOV(token)
        output += "\n\t\t\t\t\t%s" %annotate_OOV(token)
        output += "\n\t\t\t\t</token>" 
        i += 1
    output += "\n\t\t\t</tokens>"
    return output

# -----------INPUT-----------
# file to be converted
FILENAME = sys.argv[1]

# input sentences
FILENAME_INPUT = sys.argv[2]

# languages input and output
INPUT_LANG = sys.argv[3]
OUTPUT_LANG = sys.argv[4]
# ---------INPUT END---------

f = open(FILENAME, 'r')
xlf = f.read().split('\n')
f.close()

g = open(FILENAME_INPUT, 'r')
inputSnts = g.read().split('\n')
g.close()



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


xmlFiles = []
line_no = 0
# This loop converts an input format of sentences into an output XLF format.
for (line, snt_no) in xlf:
    #---------------PARSE SENTENCES---------------
    # Returns a part beginning with '(ROOT{... ...)' and ending with '-#end#-'.
    s = line.partition(' ||| ')[2].partition(' ||| ')[0] + '-#end#-'
    # Replaces textual brackets with '<open>' and '<close>'.
    # It prevents confusing textual brackets and tree brackets.
    s = s.replace('( ', '<open>').replace(' )', '<close>')

    a = 0
    nodeStrings = dict()

    # First node creation.
    node = _Node()
    # Index of actual node (used during node iteration).
    num = 1
    # Array with node indexes.
    node_no = [num]
    # Number of phrase in sentence.
    iPhraseID = 1
    node.iPhraseID = iPhraseID

    # This loop has as many iteration as count of letters in s.
    for i in range(len(s)):
        
        # If a next node starts, it creates new node and makes
        # a connection (node.parent) with a previous one.
        if re.findall('[(][[].[]]', s[i:i + 4]):
            # sNodeString - Saves each node in textual form (e. g. '[X]{3-7}').
            # It is later used in the whole sentence composition.
            node.sNodeString = node.sNodeString + '<<>>' + re.search \
                               ('[[].[]][{]\d+-\d+[}]', s[i:]).group(0)
            # Saves actual node to temp variable.
            oldnode = node
            # Creates new node.
            node = _Node()
            # Creates a connection between old node and his son.
            oldnode.add_child(node)
            # Creates a connection between new node and his father.
            node.parent = oldnode
            num = num + 1
            # Adds a node index.
            node_no.append(num)
            iPhraseID = iPhraseID + 1
            node.iPhraseID = iPhraseID

        # If a root node starts or if a next node starts.
        # (if there is: '([.]' )
        # (       s[i]-->^     )
        if re.findall('[(][[].[]]', s[i:i + 4]) or \
           re.findall('[(]ROO', s[i:i + 4]):
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
                node.sString = node.sString + replace_brackets(sText)
                # sNodeString - Saves the gained string.
                # It is later used in the whole sentence composition.
                node.sNodeString = node.sNodeString + '<<>>' + \
                                   replace_brackets(sText)

        # If a node ends.
        if s[i] == ')':
            # sString --> between } and ) or between next to last ) and last ) 
            # - Gains a string in node, if exists.
            sText = replace_brackets(s[:i].rpartition('}')[2].split(')')[-1])
            if sText:
                # sString - Saves the gained string.
                node.sString = node.sString + sText
                # sNodeString - Saves the gained string.
                # It is later used in the whole sentence composition.
                node.sNodeString = node.sNodeString + '<<>>' + sText
            # sNodeString is splitted. The list may contain string(s)
            # or node(s) in textual form (e. g. [S]{0-3}).
            node.sNodeString = node.sNodeString.strip('<<>>').split('<<>>')

            key = '[' + node.sClass + ']{' + str(node.iFrom) + '-' + \
                  str(node.iTo) + '}' 
            nodeStrings[key] = [key, node.sNodeString]
            # If node.sClass is 'ROOT', keeps ROOT node as an actual node
            # in memory (important for printing part).
            if node.sClass != 'ROOT':
                # Parent node becomes (active) node.
                node = node.parent
            node_no.pop()
    #---------------PARSE SENTENCES END---------------


    #----------COMPOSITION OF THE WHOLE TARGET LANGUAGE SENTENCE----------
    snt = ''
    # This loop gets children (in format '[S]{0-3}') of ROOT node.
    for item in nodeStrings:
        # If item is ROOT.
        if nodeStrings[item][0].count('[ROOT]'):
            # Gets one string from list of strings in ROOT.
            snt = get_str(nodeStrings[item][1])

    a = 0
    # This part of code gets the whole sentence (target language).
    while re.findall('[[].[]][{]\d+-\d+[}]', snt) and a < 1000:
        for item in re.findall('[[].[]][{]\d+-\d+[}]', snt):
            snt = snt.replace(item, get_str(nodeStrings[item][1]))
            break
        a = a + 1
    if a == 1000: print '>1000 operations in creating sentence!'
    tarSnt = snt.strip(' ')
    #----------END COMPOSITION OF THE WHOLE TARGET LANGUAGE SENTENCE----------


    #-------------CREATING AN OUTPUT FILE--------------
    sXlf = ''
    sXlf = sXlf + '\n<alt-trans tool-id="t1" add:rank="1">'
    sXlf = sXlf + '\n\t<source>' + inputSnts[line_no].strip() + '</source>'
    sXlf = sXlf + '\n\t<target>' + remove_OOV(tarSnt) + '</target>'

    # total, lm, pt0, pt1, pt2
    scores = line.rpartition('|||')[0].rpartition('|||')[2].strip().split(' ')
    # word penalty
    if len(scores) == 5:
        scores.append(line.rpartition('|||')[2].strip())
        sXlf = sXlf + '\n\t<add:scores>'
        sXlf = sXlf + '\n\t\t<score type="total" value="' + scores[5] + '" />'
        sXlf = sXlf + '\n\t\t<score type="lm" value="' + scores[0] + '" />'
        sXlf = sXlf + '\n\t\t<score type="pt0" value="' + scores[1] + '" />'
        sXlf = sXlf + '\n\t\t<score type="pt1" value="' + scores[2] + '" />'
        sXlf = sXlf + '\n\t\t<score type="pt2" value="' + scores[3] + '" />'
        sXlf = sXlf + '\n\t\t<score type="wordpenalty" value="' + scores[4] + '" />'
        sXlf = sXlf + '\n\t</add:scores>'
    
        sXlf = sXlf + '\n\t<add:derivation type="hiero_decoding" id="s' + \
               snt_no + '_t1_r1_d1">'
        chList = [node]
        while chList:
            i = 1
            # This loop adds all children of a node chList[0]
            # between chList[0] and chList[2].
            for child in chList[0].get_children():
                chList.insert(i, child)
                i = i + 1
    
            # Creates a string with a list of children.
            sChildren = ''
            if len(chList[0].get_children()):
                sChildren = ' children="'
                for child_no in chList[0].get_children():
                    sChildren = sChildren + 's' + snt_no + '_p' + \
                                str(child_no.iPhraseID) + ','
                sChildren = sChildren.strip(',') +'"'
    
            # Creates a phrase with node parameters
            # and with a node string, if exists.
            sphrase_id = 's' + snt_no + '_t1_r1_d1_p' + str(chList[0].iPhraseID)  
            sXlf = sXlf + "\n\t\t<phrase id=\"%s\" %s>" %(sphrase_id, sChildren)
            if chList[0].sString:
                sXlf += get_tokens_xml( chList[0].sString.strip(), sphrase_id )
                #sXlf = sXlf + '\n\t\t\t<string>' + replace_OOV ( chList[0].sString.strip() ) + \
                #       '</string>'
            sXlf = sXlf + '\n\t\t\t<annotation type="class" value="' + \
                   chList[0].sClass + '" />'
            sXlf = sXlf + '\n\t\t\t<alignment from="' + chList[0].iFrom + \
                   '" to="' + chList[0].iTo + '" />'
            sXlf = sXlf + '\n\t\t</phrase>'
            
            # The processed (printed) node is removed from the list.
            chList.pop(0)
    
        sXlf = sXlf + '\n\t</add:derivation>'
        sXlf = sXlf + '\n</alt-trans>'
        # Removes '\n' in the beginning of the string.
        xmlFiles.append((sXlf.strip(),snt_no))
        #-------------END CREATING AN OUTPUT FILE--------------
        # Counts iterations in main for loop.
    line_no = line_no + 1

# Creates a directory for output files.
DIR_NAME = ("t1-%s-%s" % ( INPUT_LANG, OUTPUT_LANG ))
#DIR_NAME = FILENAME.rpartition('.')[0] + time.strftime('_%y%m%d_%H%M%S') + \
#           '_output'

os.mkdir( DIR_NAME )

i = 1
# Prints output string to .xml files.
for (outputFile,sntNumber) in xmlFiles:
    
    filename = ("%s//t1-%s-%s-%.4d.xml" % ( DIR_NAME, INPUT_LANG, OUTPUT_LANG, long(sntNumber) ) )
    #h = open(DIR_NAME + '//t2-' + INPUT_LANG + '-' + OUTPUT_LANG + \
    #         '-t1-s' + sntNumbers[i] + '.xml', 'w')
    h = open(filename,'w')
    h.write(outputFile)
    h.close()
    i = i + 1
