import re, codecs
from copy import deepcopy

class Node:
    sClass = ''
    parent = None
    parentID = 0
    iFrom = 0
    iTo = 0
    sString = ''
    sChildrenD = '' # DEBUG
    parentD = '' # DEBUG
    lChildrenD = [] # DEBUG

    def __init__(self):
        self.lChildren = []
        
    def addChild(self,child):
        self.lChildren.append(child)

    def getChildren(self):
        return self.lChildren
        

def rplBrackets(string):
    return string.replace('<open>','( ').replace('<close>',' )')

def getStr(listVar):
    string = ''
    for item in listVar:
        string = string + item
    return string

# sample_pl.txt
f = open('acquis.de-pl.output.nbest.txt','r')
xml = f.read().split('\n')
f.close()

sXlf = ''
line_no = 0
for line in xml:
    line_no = line_no + 1

    s = line.partition(' ||| ')[2].partition(' ||| ')[0] + '-#end#-' # return a part beggining with '(ROOT{... ...)'
    s = s.replace('( ','<open>').replace(' )','<close>') # replace textual brackets with '<open>' and '<close>'

    # initialization
    a = 0
    lenS = len(s)
    data = dict() # DEBUG

    # first node
    node = Node() # create the first node
    node_no = [1] # DEBUG
    num = 1 # DEBUG

    for i in range(len(s)):
        
        # create next node and make a connection (node.parent) with a previous one
        if re.findall('[(][[].[]]',s[i:i+4]) != []:
            #node.lChildrenD.append(re.search('[[].[]][{]\d+-\d+[}]',s[i:]).group(0)) # DEBUG ---WHY DOES NOT FUNCTION???
            #print re.search('[(][[].[]][{]\d+-\d+[}]',s[i:]).group(0)
            # sChildrenD
            node.sChildrenD = node.sChildrenD +'<<>>'+ re.search('[[].[]][{]\d+-\d+[}]',s[i:]).group(0) # DEBUG
            oldnode = node # save actual node to temp variable
            node = Node() # create new node
            oldnode.addChild(node) # create a connection between old node and his son
            # parent
            node.parent = oldnode # create a connection between new node and his father
            node.parentD = '['+oldnode.sClass+']{'+str(oldnode.iFrom)+'-'+str(oldnode.iTo)+'}' # DEBUG
            num = num + 1 # DEBUG
            node_no.append(num) # DEBUG
                
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
            sText = s[i:].partition('}')[2].partition(' ([')[0].strip()
            if sText.count(')') == 0 and sText != '': 
                node.sString = node.sString + rplBrackets(sText)
                node.sChildrenD = node.sChildrenD +'<<>>'+rplBrackets(sText) # DEBUG
            # lChildren

        if s[i] == ')': # if closing bracket
            # sString --> between } and ) or between next to last ) and last )
            sText = rplBrackets(s[:i].rpartition('}')[2].split(')')[-1].strip())
            if sText != '':
                node.sString = node.sString + sText
                node.sChildrenD = node.sChildrenD +'<<>>'+sText # DEBUG
            # sChildrenD
            node.sChildrenD = node.sChildrenD.strip('<<>>').split('<<>>') # DEBUG
            
            key = '['+node.sClass+']{'+str(node.iFrom)+'-'+str(node.iTo)+'}' # DEBUG
            data[key] = [node_no[-1],key,node.sClass,node.iFrom,node.iTo,node.parentD,node.sChildrenD,node.sString] # DEBUG
            if node.sClass != 'ROOT': # preserve ROOT node as an actual node in memory (important for printing part)
                node = node.parent # parent node become (active) node
            node_no.pop() # DEBUG

#---------------PARSING PART END---------------
#-------------PRINTING PART BEGIN--------------

    # xlf output: ---BEGIN---

    # xlf beginning of body
    sXlf = sXlf + "\n<body>"
    sXlf = sXlf + "\n\t<trans-unit id='"+str(line_no)+"'>"
    sXlf = sXlf + "\n\t\t<source>"+'TODO'+"</source>"
    a = 0
    
    # find children of ROOT # REWORK! (by node...)
    snt = ''
    for item in data:
        if data[item][1].count('[ROOT]'):
            for child in data[item][6]:
                snt = snt + child
                #print snt
                break

    # get the whole sentence  # REWORK! (by node...)
    while re.findall('[[].[]][{]\d+-\d+[}]',snt) != [] and a < 1000:
        for item in re.findall('[[].[]][{]\d+-\d+[}]',snt):
            snt = snt.replace(item,getStr(data[item][6]))
            break
        a = a + 1
    if a == 1000: print '>1000 operations in creating sentence!'
    tarSnt = snt.strip(' ')

    sXlf = sXlf + "\n\t\t<target>"+tarSnt+"</target>"
    sXlf = sXlf + '\n\t\t<alt-trans tool-id="joshua"'+" add:rank='"+'TODO'+"'>"
    sXlf = sXlf + "\n\t\t<source>"+'TODO'+"</source>"
    sXlf = sXlf + "\n\t\t<target>"+tarSnt+"</target>"

    # xlf scores
    scores = line.rpartition('|||')[0].rpartition('|||')[2].strip().split(' ') # total, lm, pt0, pt1, pt2
    scores.append(line.rpartition('|||')[2].strip()) # add wordpenalty
    sXlf = sXlf + "\n\t\t\t<add:scores>"
    sXlf = sXlf + "\n\t\t\t\t<score type='total'>"+scores[0]+"</score>"
    sXlf = sXlf + "\n\t\t\t\t<score type='lm'>"+scores[1]+"</score>"
    sXlf = sXlf + "\n\t\t\t\t<score type='pt0'>"+scores[2]+"</score>"
    sXlf = sXlf + "\n\t\t\t\t<score type='pt1'>"+scores[3]+"</score>"
    sXlf = sXlf + "\n\t\t\t\t<score type='pt2'>"+scores[4]+"</score>"
    sXlf = sXlf + "\n\t\t\t<score type='wordpenalty'>"+scores[5]+"</score>"
    sXlf = sXlf + "</add:scores>"

    # xlf derovation
    sXlf = sXlf + '\n\t\t\t<add:derivation type="hiero_decoding">'
    chList = [node]
    phraseID = 1
    while chList != []:
        i = 1
        for child in chList[0].getChildren():
            child.parentID = phraseID
            chList.insert(i,child)
            i = i + 1
        sXlf = sXlf + "\n\t\t\t\t<phrase id='"+str(phraseID)+"'>"
        if chList[0].sString != '': sXlf = sXlf + '\n\t\t\t\t\t<string>'+chList[0].sString+'</string>'
        sXlf = sXlf + '\n\t\t\t\t\t<annotation type="class">'+chList[0].sClass+'</annotation>'
        sXlf = sXlf + '\n\t\t\t\t\t<annotation type="alignment" from="'+chList[0].iFrom+'", to="'+chList[0].iTo+'"))" />'
        if chList[0].parentID != 0: sXlf = sXlf + '\n\t\t\t\t\t<annotation type="parent" ref-id="'+str(chList[0].parentID)+'" />'
        sXlf = sXlf + '\n\t\t\t\t</phrase>'
        chList.pop(0)
        phraseID = phraseID + 1
    sXlf = sXlf + '\n\t\t\t</add:derivation>'
    sXlf = sXlf + '\n\t\t</alt-trans>'
    sXlf = sXlf + '\n\t</trans-unit>'
    sXlf = sXlf + '\n</body>'
    sXlf = sXlf.strip()
    # xlf output: ---END---
    
    #print 'node number,key,class,from,to,parent,children,string' # DEBUG
    for key in data:
        #print data[key],'\n'
        pass

    # iteration menu:
    if line_no % 100 == 0:
        print line_no
        break
    if line_no == 5:
        print '>10000 lines in file!'
        break

print sXlf
h = open('oXf', 'w')
h.write(sXlf)
h.close()
