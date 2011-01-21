"""
This version prints the best version of each sentence to a single file.
"""
import re, codecs, os, time, sys
from copy import deepcopy

class Node:
    sClass = ''
    parent = None
    phraseID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    sNodeString = '' # e. g. '[X]{12-14} zmiany :' or '[X]{7-12} jutro ([X]{9-12} wprowadza) nie'

    def __init__(self):
        self.lChildren = []
        
    def addChild(self,child):
        self.lChildren.append(child)

    def getChildren(self):
        return self.lChildren
        
# replace tags for brackets (prevention of bracket misunderstanding) 
def rplBrackets(string):
    return string.replace('<open>','( ').replace('<close>',' )')


def getStr(listVar):
    string = ''
    for item in listVar:
        string = string + item
    return string

# -----------INPUT-----------
# joshua.xlf conversion file
# small_pl.txt, n.nbest, acquis.de-pl.output.nbest.txt
filename = 'acquis.de-pl.output.nbest.txt'

# input sentences
# acquis.dev.de
filenameInput = 'acquis.dev.de'

# languages input & output
input_lang = 'de'
output_lang = 'pl'
# ---------INPUT END---------

f = open(filename,'r')
xlf = f.read().split('\n')
f.close()

g = open(filenameInput,'r')
inputSnts = g.read().split('\n')
g.close()

#-------SELECT SENTENCES-------
# select the best sentences according to the wordpenalty

# add all sentences to dict d
bestSnts = []
d = {}
for snt in xlf:
    snt_no = snt.partition(' ||| ')[0] # sentence number
    snt_wp = snt.rpartition(' ||| ')[2] # sentence wordpenalty
    if snt_no in d: # if a key 'snt_no' already created in d
        d[snt_no].append([snt_wp, snt]) # add [word penalty, sentence] to a proper sentence number
    else:
        d[snt_no] = [] # create a key in d
        d[snt_no].append([snt_wp, snt])

# select the best sentence from dict d
sntNumbers = d.keys()
for sntNo in sntNumbers:
    minWP = sys.maxint # initialization of minimal word penalty index for each sentence
    snt = ''
    for elem in d[sntNo]:
        if abs(float(elem[0])) < minWP:
            minWP = abs(float(elem[0]))
            snt = elem[1]
    bestSnts.append(snt)
#-----END SELECT SENTENCES-----

#---------------PARSE SENTENCES---------------
xmlFiles = [] # global var for each xml output file
line_no = 0
for line in bestSnts:
    line_no = line_no + 1

    s = line.partition(' ||| ')[2].partition(' ||| ')[0] + '-#end#-' # return a part beggining with '(ROOT{... ...)'
    s = s.replace('( ','<open>').replace(' )','<close>') # replace textual brackets with '<open>' and '<close>'

    # initialization
    a = 0
    lenS = len(s)
    nodeStrings = dict()

    # first node
    node = Node() # create the first node
    num = 1 # index of actual node (used during node iteration)
    node_no = [num] # stack [zasobnik] of node indexes
    phraseID = 1 # number of phrase in sentence
    node.phraseID = phraseID

    for i in range(len(s)):
        
        # create next node and make a connection (node.parent) with a previous one
        if re.findall('[(][[].[]]',s[i:i+4]) != []:
            # sNodeString
            node.sNodeString = node.sNodeString +'<<>>'+ re.search('[[].[]][{]\d+-\d+[}]',s[i:]).group(0)
            oldnode = node # save actual node to temp variable
            node = Node() # create new node
            oldnode.addChild(node) # create a connection between old node and his son
            # parent
            node.parent = oldnode # create a connection between new node and his father
            num = num + 1
            node_no.append(num)
            phraseID = phraseID + 1
            node.phraseID = phraseID
                
        # if there is: '([.]'
        #        s[i]-->^
        if re.findall('[(][[].[]]',s[i:i+4]) != [] or re.findall('[(]ROO',s[i:i+4]) != []:
            # sClass
            node.sClass = re.search('[A-Z]+',s[i:i+5]).group(0)
            # iFrom
            node.iFrom = re.match('.*?(\d+)-(\d+).*?',s[i:i+14]).group(1)
            # iTo
            node.iTo = re.match('.*?(\d+)-(\d+).*?',s[i:i+14]).group(2)
            # sString --> between } and ([
            sText = s[i:].partition('}')[2].partition(' ([')[0]#.strip() 
            if sText.count(')') == 0 and sText != '':
                # sString
                node.sString = node.sString + rplBrackets(sText)
                # sNodeString
                node.sNodeString = node.sNodeString +'<<>>'+rplBrackets(sText)

        if s[i] == ')': # if closing bracket
            # sString --> between } and ) or between next to last ) and last )
            sText = rplBrackets(s[:i].rpartition('}')[2].split(')')[-1])#.strip()
            if sText != '':
                # sString
                node.sString = node.sString + sText
                # sNodeString                
                node.sNodeString = node.sNodeString +'<<>>'+sText
            # sNodeString
            node.sNodeString = node.sNodeString.strip('<<>>').split('<<>>')
            
            key = '['+node.sClass+']{'+str(node.iFrom)+'-'+str(node.iTo)+'}' # create key (string with node description)
            nodeStrings[key] = [key,node.sNodeString]
            if node.sClass != 'ROOT': # preserve ROOT node as an actual node in memory (important for printing part)
                node = node.parent # parent node become (active) node
            node_no.pop()

#---------------PARSE SENTENCES END---------------
#-------------PRINTING PART--------------

    # find child of ROOT...
    snt = ''
    for item in nodeStrings: # for each nodeString
        if nodeStrings[item][0].count('[ROOT]'): # if nodeString is ROOT
            for child in nodeStrings[item][1]: # for each child of ROOT
                snt = snt + child
                
    a = 0
    # ...and get the whole sentence (output language)
    while re.findall('[[].[]][{]\d+-\d+[}]',snt) != [] and a < 1000:
        for item in re.findall('[[].[]][{]\d+-\d+[}]',snt):
            snt = snt.replace(item,getStr(nodeStrings[item][1]))
            break
        a = a + 1
    if a == 1000: print '>1000 operations in creating sentence!'
    tarSnt = snt.strip(' ')

    sXlf = ''
    sXlf = sXlf + '\n<alt-trans tool-id="t1" add:rank="1">'
    sXlf = sXlf + '\n\t<source>'+inputSnts[line_no-1].strip()+'</source>'
    sXlf = sXlf + '\n\t<target>'+tarSnt+'</target>'

    # xlf scores
    scores = line.rpartition('|||')[0].rpartition('|||')[2].strip().split(' ') # total, lm, pt0, pt1, pt2
    scores.append(line.rpartition('|||')[2].strip()) # add wordpenalty
    sXlf = sXlf + '\n\t<add:scores>'
    sXlf = sXlf + '\n\t\t<score type="total" value="'+scores[0]+'" />'
    sXlf = sXlf + '\n\t\t<score type="lm" value="'+scores[1]+'" />'
    sXlf = sXlf + '\n\t\t<score type="pt0" value="'+scores[2]+'" />'
    sXlf = sXlf + '\n\t\t<score type="pt1" value="'+scores[3]+'" />'
    sXlf = sXlf + '\n\t\t<score type="pt2" value="'+scores[4]+'" />'
    sXlf = sXlf + '\n\t<score type="wordpenalty" value="'+scores[5]+'" />'
    sXlf = sXlf + '\n</add:scores>'

    # xlf derivation
    sXlf = sXlf + '\n\t<add:derivation type="hiero_decoding" id="s'+str(line_no)+'_t2">'
    chList = [node]
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
                sChildren = sChildren+'s'+str(line_no)+'_p'+str(child_no.phraseID)+','
            sChildren = sChildren.strip(',')+'"'
        # print
        sXlf = sXlf + '\n\t\t<phrase id="s'+str(line_no)+'_t1_p'+str(chList[0].phraseID)+'"'+sChildren+'>'
        if chList[0].sString != '': sXlf = sXlf + '\n\t\t\t<string>'+chList[0].sString.strip()+'</string>'
        sXlf = sXlf + '\n\t\t\t<annotation type="class" value="'+chList[0].sClass+'" />'
        sXlf = sXlf + '\n\t\t\t<alignment from="'+chList[0].iFrom+'" to="'+chList[0].iTo+'" />'
        sXlf = sXlf + '\n\t\t</phrase>'
        chList.pop(0)
    sXlf = sXlf + '\n\t</add:derivation>'
    sXlf = sXlf + '\n</alt-trans>'
    xmlFiles.append(sXlf.strip()) # remove '\n' in the beginning of the string

# create a directory
dirName = filename.rpartition('.')[0]+time.strftime('_%y%m%d_%H%M%S')+'_output'
os.mkdir(dirName)

i = 0
#print output to .xml files
for outputFile in xmlFiles:
    h = open(dirName+'//trans-unit-'+input_lang+'-'+output_lang+'-t1-s'+sntNumbers[i]+'.xml', 'w')
    h.write(outputFile)
    h.close()
    i = i + 1

#-------------PRINTING PART END--------------
