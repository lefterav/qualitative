"""
This module converts sentences from bad file to xml files. There is only one
sentence in each newly generated xml file.
"""
import re
import os
import sys
import time
from copy import deepcopy

class _Node:
    sClass = ''
    parent = None
    iSegmentID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    sCAN = ''
    sCAT = ''
    sALO = ''
    sSL_CAN = ''
    sTL_CAN = ''
    sSL_CAT = ''
    sTL_CAT = ''


    def __init__(self):
        self.lChildren = []

    def add_child(self, child):
        self.lChildren.append(child)

    def get_children(self):
        return self.lChildren


# This method looks for "CAN " in a node. If found, it returns a string that
# follows "CAN ". If doesn't found, it returns an empty string.
def get_CAN(sgt):
    if sgt.count('CAN "'):
        return sgt.partition('CAN "')[2].partition('"')[0]
    else:
        return ''


# This method looks for "CAT " in a node. If found, it returns a string that
# follows "CAT ". If doesn't found, it returns an empty string.
def get_CAT(sgt):
    if sgt.count('CAT '):
        return sgt.partition('CAT ')[2].partition(' ')[0]
    else:
        return ''


# This method looks for "ALO " in a node. If found, it returns a string that
# follows "ALO ". If doesn't found, it returns an empty string.
def get_ALO(sgt):
    if sgt.count('ALO "'):
        return sgt.partition('ALO "')[2].partition('"')[0]
    else:
        return ''


# This method looks for "SL-CAN " in a node. If found, it returns a string that
# follows "SL-CAN ". If doesn't found, it returns an empty string.
def get_SL_CAN(sgt):
    if sgt.count('SL-CAN "'):
        return sgt.partition('SL-CAN "')[2].partition('"')[0]
    else:
        return ''


# This method looks for "TL-CAN " in a node. If found, it returns a string that
# follows "TL-CAN ". If doesn't found, it returns an empty string.
def get_TL_CAN(sgt):
    if sgt.count('TL-CAN "'):
        return sgt.partition('TL-CAN "')[2].partition('"')[0]
    else:
        return ''


# This method looks for "SL-CAT " in a node. If found, it returns a string that
# follows "SL-CAT ". If doesn't found, it returns an empty string.
def get_SL_CAT(sgt):
    if sgt.count('SL-CAT '):
        return sgt.partition('SL-CAT ')[2].partition(' ')[0]
    else:
        return ''


# This method looks for "TL-CAT " in a node. If found, it returns a string that
# follows "TL-CAT ". If doesn't found, it returns an empty string.
def get_TL_CAT(sgt):
    if sgt.count('TL-CAT '):
        return sgt.partition('TL-CAT ')[2].partition(' ')[0]
    else:
        return ''


# This code replaces round brackets by '{<{', ev. '}>}'. The aim is 
# to distinguish text brackets and brackets that are used as a node separators.
# example: before: '...ALO "aber (ja)") ((CAN...'
#          after:  '...ALO "aber {<{ja}>}") ((CAN...'
def replace_brackets(s):
    brTxt = re.findall(' "[^"]*[)][^"]*"', s) # find textual ")"
    brTxt.extend(re.findall(' "[^"]*[(][^"]*"', s)) # find textual "("
    for item in set(brTxt):
        itemR = item.replace('(', '{<{').replace(')', '}>}')
        s = s.replace(item, itemR)
    return s


# -----INPUT------
FILENAME = 'lucy.de-en.1000.bad'
FILENAME_INPUT = 'test2008.1000.tok.de'
FILENAME_OUTPUT = 'lucy.de-en.1000.txt'
INPUT_LANG = 'de'
OUTPUT_LANG = 'en'
# ----END INPUT----

g = open(FILENAME, 'r')
s = g.read().replace('\n', ' ')
g.close()

h = open(FILENAME_INPUT, 'r')
iSnts = h.readlines()
h.close()

a = open(FILENAME_OUTPUT, 'r')
oSnts = a.readlines()
a.close()

# Replaces round textual brackets by '{<{', ev. '}>}'.
s = replace_brackets(s)

# This code checks parentness in a source text.
if s.count(')') != s.count('('):
    print 'Parenthness error!'

# This code splits the src text to analysis-, transfer- and generation-part.
parts = []
parts.append(s.partition('<analysis>')[2].partition('</analysis>')[0])
parts.append(s.partition('<transfer>')[2].partition('</transfer>')[0])
parts.append(s.partition('<generation>')[2].partition('</generation>')[0])

# This code creates an output folder. Folder name consists of source file name
# and actual time.
DIR_NAME = '%s%s_output' % (FILENAME.rpartition('.')[0],
                            time.strftime('_%y%m%d_%H%M%S'))
os.mkdir(DIR_NAME)

# The variable d determines a part of the source text ('1' = analysis, 
# '2' = transfer, '3' = generation)
d = 0
# The variable sD contains a name of source text part (e. g. 'analysis')
sD = ''
# There are 3 iterations in this loop: for analysis part, transfer part and
# generation part.
for part in parts:
    d += 1
    if d == 1:
        sD = 'analysis'
    if d == 2:
        sD = 'transfer'
    if d == 3:
        sD = 'generation'
    o = 0
    c = 0
    blocks = []
    ws = ''
    sXlf = ''
    # This loop uses the parent-child structure of the source text and splits
    # the text into blocks. These blocks are in fact separated trees
    # with parent-child structure. Each block contains one sentence.
    for char in part:
        # Adds next character to the block.
        ws += char
        # Counts number of opened brackets.
        if char == '(':
            o += 1
        # Counts number of closed brackets.
        if char == ')':
            c += 1
        # Explanations of conditions:
        # (o == c): All opened brackets are closed (i.e. end of the block).
        # (o != 0): The "cursor" is not in the very beginning.
        # (char == ')'): exclude multiple saving of the same segment
        if o == c and o > 0 and char == ')':
            # This is an indicator for block ending.
            ws += '-#end#-'
            # Adds sentence to sentence list.
            blocks.append(ws)
            ws = ''

    # This code gets information block and sentences count during program run.
    print '%s - no. of blocks in %s is %s.' % (sD.capitalize(), FILENAME, 
                                               str(len(blocks)))
    print 'No. of input sentences in %s is %s.' % (FILENAME_INPUT,
                                                   str(len(iSnts)))
    print 'No. of output sentences in %s is %s.' % (FILENAME_OUTPUT,
                                                    str(len(oSnts)))

    stop = sys.maxint
    # If count of blocks in the source file is higher than count of source or
    # target language sentences, not all blocks will be processed.
    # In this case a user gets a warning.
    if len(blocks) > len(iSnts) or len(blocks) > len(oSnts):
        print 'Warning: Number of input or output sentences in %s or %s is ' \
              'lower than number of blocks in %s!!!' % \
              (FILENAME_INPUT, FILENAME_OUTPUT, FILENAME)
        # Variable stop sets a limit of blocks that will be processed.
        stop = min(len(iSnts), len(oSnts))

    # This code iterates blocks (separated trees with parent-child structure).
    # The block structure is transformed into xml format and saved to a file.
    # As a rule there is one file per one sentence.
    block_no = 0
    for block in blocks:
        block_no += 1
        
        # This condition stops creating of xml files, if there is not enough
        # source of target language sentences.
        if block_no > stop:
            break
            
        node = _Node()
        iSegmentID = 1
        # This loop iterates particular characters in a block.
        for i in range(len(block)):
            # This condition indicates node begin (segment begin).
            if block[i:i + 2] == '((':
                # Saves actual node to temp variable.
                oldnode = node
                # Creates new node.
                node = _Node()
                # Creates a connection between old and new node (parent-child).
                oldnode.add_child(node)
                # Creates a connection between new and old node (child-parent).
                node.parent = oldnode
                # Gets the whole segment.
                sgt = block[i:].partition(')')[0].strip('(')
                # Returns round brackets to segment. In the beginning round
                # brackets were replaced by '{<{', resp. '}>}' to distinguish
                # between textual brackets and parent-child-structure brackets.
                sgt = sgt.replace('{<{', '(').replace('}>}', ')')
                # All attributes of one segment are saved to actual node class.
                node.sCAN = get_CAN(sgt)
                node.sCAT = get_CAT(sgt)
                node.sALO = get_ALO(sgt)
                node.sSL_CAN = get_SL_CAN(sgt)
                node.sTL_CAN = get_TL_CAN(sgt)
                node.sSL_CAT = get_SL_CAT(sgt)
                node.sTL_CAT = get_TL_CAT(sgt)
                node.iSegmentID = iSegmentID
                # Counts segment in one block.
                iSegmentID += 1
            # This condition indicates end of block.
            if block[i:i + 2] == '))':
                # Parent node become (active) node ("go back to ROOT").
                node = node.parent

        sContent = ''
        # If it is the first part (analysis), it creates xml head and all
        # beginning tags.
        if d == 1:
            sContent += '<trans-unit id="%s">' % (str(block_no))
            sContent += '\n\t<source>%s</source>' % (iSnts[block_no-1].strip())
            sContent += '\n\t<target>%s</target>' % (oSnts[block_no-1].strip())
            sContent += '\n\t<alt-trans tool-id="t2">'
            sContent += '\n\t\t<source>%s</source>'%(iSnts[block_no-1].strip())
            sContent += '\n\t\t<target>%s</target>'%(oSnts[block_no-1].strip())
                       
        sContent += '\n\t\t<add:derivation type="lucy%s" id="s%s_t2_d%s">' % \
                    (sD, str(block_no), str(d))
                   
        # Adds the first node (root node) to chList.
        chList = node.get_children()
        # This loop creates a string in a required xml format for one block.
        while chList:
            i = 1
            # This loop adds all children of node chList[0] between chList[0]
            # and chList[2].
            for child in chList[0].get_children():
                chList.insert(i, child)
                i = i + 1
            sChildren = ''
            # If the node has some children, an output string
            # with "children addresses" is created.
            if chList[0].get_children():
                sChildren = ' children="'
                for child_no in chList[0].get_children():
                    sChildren = '%ss%s_t2_d%s_k%s,' % (sChildren, \
                               str(block_no), str(d), str(child_no.iSegmentID))
                sChildren = '%s"' % (sChildren.strip(','))
            # This code prints all information about a node in a required xml
            # format.
            sTemp = ''
            sTemp += '\n\t\t\t<token id="s%s_t2_d%s_k%s" %s>' % \
                  (str(block_no), str(d), str(chList[0].iSegmentID), sChildren)
            if chList[0].sCAN:
                sTemp += '\n\t\t\t\t<annotationtype="can" value="%s" />' % \
                         (chList[0].sCAN)
            if chList[0].sCAT:
                sTemp += '\n\t\t\t\t<annotationtype="cat" value="%s" />' % \
                         (chList[0].sCAT)
            if chList[0].sALO:
                sTemp += '\n\t\t\t\t<annotationtype="alo" value="%s" />' % \
                         (chList[0].sALO)
            if chList[0].sSL_CAN:
                sTemp += '\n\t\t\t\t<annotationtype="sl-can" value="%s" />' % \
                         (chList[0].sSL_CAN)
            if chList[0].sTL_CAN:
                sTemp += '\n\t\t\t\t<annotationtype="tl-can" value="%s" />' % \
                         (chList[0].sTL_CAN)
            if chList[0].sSL_CAT:
                sTemp += '\n\t\t\t\t<annotationtype="sl-cat" value="%s" />' % \
                         (chList[0].sSL_CAT)
            if chList[0].sTL_CAT:
                sTemp += '\n\t\t\t\t<annotationtype="tl-cat" value="%s" />' % \
                         (chList[0].sTL_CAT)
            sTemp += '\n\t\t\t</token>'
            # Removes already processed node.
            chList.pop(0)
            sContent += sTemp
            
        sContent += '\n\t\t</add:derivation>'

        # If it is the last part (generation), it creates xml all closing tags.
        if d == 3:
            sContent += '\n\t</alt-trans>'
            sContent += '\n</trans-unit>'
            
        # A number is printed for each 100 blocks.
        if block_no % 100 == 0:
            print '%s blocks processed.' % (str(block_no))
        
        # Prints the parsed block to a xml file.
        output_type = ''
        if d == 1:
            output_type = 'w'
        if d == 2 or d == 3:
            output_type = 'r+'
        h = open('%s//trans-unit-%s-%s-t2-s%s.xml' % (DIR_NAME, INPUT_LANG, \
                                      OUTPUT_LANG, str(block_no)), output_type)
        h.seek(0,2)
        h.write(sContent)
        h.close()
