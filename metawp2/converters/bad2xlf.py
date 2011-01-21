import re, time, os, sys
from copy import deepcopy

class Node:
    sClass = ''
    parent = None
    phraseID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    CAN = ''
    CAT = ''
    ALO = ''
    SL_CAN = ''
    TL_CAN = ''
    SL_CAT = ''
    TL_CAT = ''


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

def getSL_CAN(sgt):
    if sgt.count('SL-CAN "') > 0:
        return sgt.partition('SL-CAN "')[2].partition('"')[0]
    else: return ''

def getTL_CAN(sgt):
    if sgt.count('TL-CAN "') > 0:
        return sgt.partition('TL-CAN "')[2].partition('"')[0]
    else: return ''

def getSL_CAT(sgt):
    if sgt.count('SL-CAT ') > 0:
        return sgt.partition('SL-CAT ')[2].partition(' ')[0]
    else: return ''

def getTL_CAT(sgt):
    if sgt.count('TL-CAT ') > 0:
        return sgt.partition('TL-CAT ')[2].partition(' ')[0]
    else: return ''

# -----INPUT------
# sample_analysis.txt, sample_transfer.txt, lucy.de-en.bad
filename = 'lucy.de-en.1000.bad'
filenameInput = 'test2008.1000.tok.de'
filenameOutput = 'lucy.de-en.1000.txt'
input_lang = 'de'
output_lang = 'en'
#----END INPUT----
g = open(filename, 'r')
s = g.read().replace('\n',' ')
g.close()

h = open(filenameInput, 'r')
iSnts = h.readlines()
h.close()

a = open(filenameOutput, 'r')
oSnts = a.readlines()
a.close()

# replace round brackets by '{<{', ev. '}>}' to distinguish text brackets and 'tree' bracktes
# example: '...ALO "aber (ja)") ((CAN...' --> '...ALO "aber {<{ja}>}") ((CAN...'
brTxt = re.findall(' "[^"]*[)][^"]*"',s) # find all "...)..."
brTxt.extend(re.findall(' "[^"]*[(][^"]*"',s)) # find all "...(..."
for item in set(brTxt):
    itemR = item.replace('(','{<{').replace(')','}>}')
    s = s.replace(item,itemR)

# check parentness
if s.count(')') != s.count('('): print 'parenthness error!'

# split the input file to 3 parts: analysis, transfer and generation
parts = []
parts.append(s.partition('<analysis>')[2].partition('</analysis>')[0])
parts.append(s.partition('<transfer>')[2].partition('</transfer>')[0])
parts.append(s.partition('<generation>')[2].partition('</generation>')[0])

# create an output directory
dirName = filename.rpartition('.')[0]+time.strftime('_%y%m%d_%H%M%S')+'_output'
os.mkdir(dirName)

d = 0 # a part ('1' = analysis, '2' = transfer, '3' = generation)
sD = '' # a part by word
for part in parts:
    d = d + 1
    if d == 1: sD = 'analysis'
    if d == 2: sD = 'transfer'
    if d == 3: sD = 'generation'
    # split the part of file into sentences
    o = 0
    c = 0
    snts = [] # sentences
    ws = ''
    sXlf = ''
    for char in part:
        ws = ws + char # add character to the sentence
        if char == '(': o = o + 1 # counts number of opened brackets
        if char == ')': c = c + 1 # counts number of closed brackets
        # (o == c):all opened brackets are closed (i.e. a segment is finished); (o != 0):it is not in the beginning; (char == ')'): exclude multiple saving of the same segment
        if o == c and o != 0 and char == ')':
            ws = ws + '-#end#-' # sentence ending
            snts.append(ws) # add sentence to sentence list
            ws = '' # clean variable for the next sentence

    # info
    print sD,'- number of sentences in',filename,'is',len(snts)
    print 'number of input sentences in',filenameInput,'is',len(iSnts)
    print 'number of output sentences in',filenameOutput,'is',len(oSnts)
    stop = sys.maxint
    if len(snts) > len(iSnts) or len(snts) > len(oSnts):
        print 'Warning: Number of input or output sentences in',filenameInput,'or',filenameOutput,'is lower than number of sentences in',filename,'!!!'
        stop = min(len(iSnts),len(oSnts))

    # get all nodes and their attributes for each sentence
    snt_no = 0 # DEBUG
    sTemp3 = '' # temporary variable for output saving
    for snt in snts: # for each sentence
        snt_no = snt_no + 1
        #print snt_no
        if snt_no > stop: # if 
            break
        node = Node() # create the first node
        phraseID = 1
        for i in range(len(snt)): # for each character in sentence
            if snt[i:i+2] == '((': # node begin
                oldnode = node # save actual node to temp variable
                node = Node() # create new node
                oldnode.addChild(node) # create a connection between old node and his son
                node.parent = oldnode # create a connection between new node and his father
                sgt = snt[i:].partition(')')[0].strip('(').replace('{<{','(').replace('}>}',')') # parsed segment from sentence
                node.CAN = getCAN(sgt)
                node.CAT = getCAT(sgt)
                node.ALO = getALO(sgt)
                node.SL_CAN = getSL_CAN(sgt)
                node.TL_CAN = getTL_CAN(sgt)
                node.SL_CAT = getSL_CAT(sgt)
                node.TL_CAT = getTL_CAT(sgt)
                node.phraseID = phraseID
                phraseID = phraseID + 1
            if snt[i:i+2] == '))': # node end
                node = node.parent # parent node become (active) node

#---------------PARSING PART END---------------
#-------------PRINTING PART BEGIN--------------

        sContent = '' # temporary variable for each part (analysis, transfer, generation)
        # if first part
        if d == 1:
            # print a file head and all beginning tags
            sContent = sContent + '<trans-unit id="'+str(snt_no)+'">'
            sContent = sContent + '\n\t<source>'+iSnts[snt_no-1].strip()+'</source>'
            sContent = sContent + '\n\t<target>'+oSnts[snt_no-1].strip()+'</target>'
            sContent = sContent + '\n\t<alt-trans tool-id="t2">'
            sContent = sContent + '\n\t\t<source>'+iSnts[snt_no-1].strip()+'</source>'
            sContent = sContent + '\n\t\t<target>'+oSnts[snt_no-1].strip()+'</target>'

        sContent = sContent + '\n\t\t<add:derivation type="lucy'+sD+'" id="s'+str(snt_no)+'_t2_d'+str(d)+'">'
        
        chList = node.getChildren() # first node (root)
        while chList != []:
            i = 1
            # for loop: add all children of node chList[0] between chList[0] and chList[2]
            for child in chList[0].getChildren():
                chList.insert(i,child)
                i = i + 1
            # create children output
            sChildren = ''
            if len(chList[0].getChildren()) > 0:
                sChildren = ' children="'
                for child_no in chList[0].getChildren():
                    sChildren = sChildren+'s3_t1_d'+str(d)+'_k'+str(child_no.phraseID)+','
                sChildren = sChildren.strip(',')+'"'
            sTemp = '' # temporary variable for output saving
            sTemp = sTemp + '\n\t\t\t<token id="s'+str(snt_no)+'_t2_d'+str(d)+'_k'+str(chList[0].phraseID)+'" '+sChildren+'>'
            if chList[0].CAN != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="can" value="'+chList[0].CAN+'" />'
            if chList[0].CAT != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="cat" value="'+chList[0].CAT+'" />'
            if chList[0].ALO != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="alo" value="'+chList[0].ALO+'" />'
            if chList[0].SL_CAN != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="sl-can" value="'+chList[0].SL_CAN+'" />'
            if chList[0].TL_CAN != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="tl-can" value="'+chList[0].TL_CAN+'" />'
            if chList[0].SL_CAT != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="sl-cat" value="'+chList[0].SL_CAT+'" />'
            if chList[0].TL_CAT != '': sTemp = sTemp + '\n\t\t\t\t<annotationtype="tl-cat" value="'+chList[0].TL_CAT+'" />'
            sTemp = sTemp + '\n\t\t\t</token>'
            chList.pop(0) # remove already printed node
            sContent = sContent + sTemp
            
        sContent = sContent + '\n\t\t</add:derivation>'

        # if last part
        if d == 3:
            # print all closing tags
            sContent = sContent + '\n\t</alt-trans>'
            sContent = sContent + '\n</trans-unit>'
# --------------write results to the file--------------
        if snt_no % 100 == 0: print snt_no
        output_type = ''
        if d == 1: output_type = 'w'
        if d == 2 or d == 3: output_type = 'r+'
        h = open(dirName+'//trans-unit-'+input_lang+'-'+output_lang+'-t2-s'+str(snt_no)+'.xml',output_type)
        h.seek(0,2) # go to the last character with a cursor
        h.write(sContent)
        h.close()
