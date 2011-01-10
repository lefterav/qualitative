import re
from copy import deepcopy

class Node:
    sClass = ''
    parent = None
    parentID = 0
    phraseID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    CAN = ''
    CAT = ''
    ALO = ''

    def __init__(self):
        self.lChildren = []
        
    def addChild(self,child):
        self.lChildren.append(child)

    def getChildren(self):
        return self.lChildren

def getCAN(sgt):
    if sgt.count('CAN "') > 0: return sgt.partition('CAN "')[2].partition('"')[0]
    else: return ''

def getCAT(sgt):
    if sgt.count('CAT ') > 0:
        return sgt.partition('CAT ')[2].partition(' ')[0]
    else: return ''

def getALO(sgt):
    if sgt.count('ALO "') > 0:
        return sgt.partition('ALO "')[2].partition('"')[0]
    else: return ''

# sample_src_1.txt, lucy.de-en.bad
filename = 'lucy.de-en.bad'
g = open(filename, 'r')
s = g.read().replace('\n',' ')
g.close()

# replace round brackets by '{<{', ev. '}>}' to distinguish text brackets and 'tree' bracktes
# example: '...ALO "aber (ja)") ((CAN...' --> '...ALO "aber {<{ja}>}") ((CAN...'
brTxt = re.findall(' "[^"]*[)][^"]*"',s) # find all "...)..."
brTxt.extend(re.findall(' "[^"]*[(][^"]*"',s)) # find all "...(..."
for item in set(brTxt):
    itemR = item.replace('(','{<{').replace(')','}>}')
    s = s.replace(item,itemR)

# check parentness
if s.count(')') != s.count('('): print 'parenthness error!'

# split the whole file into segments
o = 0
c = 0
snts = [] # sentences
ws = ''
sXlf = ''
for char in s:
    ws = ws + char # add character to the sentence
    if char == '(': o = o + 1 # counts number of opened brackets
    if char == ')': c = c + 1 # counts number of closed brackets
    # (o == c):all opened brackets are closed (i.e. a segment is finished); (o != 0):it is not in the beginning; (char == ')'): exclude multiple saving of the same segment
    if o == c and o != 0 and char == ')':
        ws = ws + '-#end#-' # sentence ending
        snts.append(ws) # add sentence to sentence list
        ws = '' # clean variable for the next sentence
        #if len(snts) == 10: # REMOVE TO PROCESS THE WHOLE FILE
        #    break

print 'number of sentences:',len(snts) # DEBUG
# get all nodes and their attributes for each sentence
#snt_no = 0 # DEBUG
sTemp3 = '' # temporary variable for output saving
for snt in snts: # for each sentence
    node = Node() # create the first node
    phraseID = 1
    snt_no = snt_no + 1
    #print 'sentence:',snt_no # DEBUG
    for i in range(len(snt)): # for each character in sentence
        if snt[i:i+2] == '((': # node begin
            oldnode = node # save actual node to temp variable
            node = Node() # create new node
            oldnode.addChild(node) # create a connection between old node and his son
            node.parent = oldnode # create a connection between new node and his father
            node.parentID = oldnode.phraseID # save ID of parent node
            sgt = snt[i:].partition(')')[0].strip('(').replace('{<{','(').replace('}>}',')') # parsed segment from sentence
            node.CAN = getCAN(sgt)
            node.CAT = getCAT(sgt)
            node.ALO = getALO(sgt)
            node.phraseID = phraseID
            phraseID = phraseID + 1
        if snt[i:i+2] == '))': # node end
            node = node.parent # parent node become (active) node

#---------------PARSING PART END---------------
#-------------PRINTING PART BEGIN--------------

# xlf output: ---BEGIN---
    chList = node.getChildren() # first node (root)
    sTemp2 = '' # temporary variable for output saving
    while chList != []:
        i = 1
        # for loop: add all children of node chList[0] between chList[0] and chList[2]
        for child in chList[0].getChildren():
            chList.insert(i,child)
            i = i + 1
        # write output
        sTemp = '' # temporary variable for output saving
        sTemp = sTemp + "\n<phraseid='"+str(chList[0].phraseID)+"'>"
        if chList[0].CAN != '': sTemp = sTemp + '\n\t<annotationtype="can">'+chList[0].CAN+'</annotation>'
        if chList[0].CAT != '': sTemp = sTemp + '\n\t<annotationtype="cat">'+chList[0].CAT+'</annotation>'
        if chList[0].ALO != '': sTemp = sTemp + '\n\t<annotationtype="alo">'+chList[0].ALO+'</annotation>'
        if chList[0].parentID != 0: sTemp = sTemp + '\n\t<annotationtype="parent"'+"ref-id='"+str(chList[0].parentID)+"'/>"
        sTemp = sTemp + "\n</phrase>"
        chList.pop(0) # remove already printed node
        sTemp2 = sTemp2 + sTemp
    sTemp3 = sTemp3 + sTemp2
    # using of 3 'temp' variables and following if condition makes the script faster
    if len(sTemp3) > 1000000:
        sXlf = sXlf + sTemp3
        sTemp3 = ''
sXlf = sXlf.strip() # remove '\n' in the beginning of the string
# xlf output: ---END---

# write results
h = open('o_'+filename,'w')
h.write(sXlf)
h.close()
