#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from copy import deepcopy

class Node:

    sClass = ''
    parent = None
    iFrom = 0
    iTo = 0
    #lChildren = []
    sString = ''
    sChildrenD = '' # DEBUG
    parentD = '' # DEBUG
    #lChildrenD = [] # DEBUG
    
    

    def __init__(self):
        self.lChildren = []
        self.lChildrenD = []
        
    def addChild(self, child):
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

f = open('acquis.de-pl.output.nbest','r')
xml = f.read().split('\n')
f.close()

output = ''
line_no = 0
for line in xml:
    line_no = line_no + 1

    s = line.partition(' ||| ')[2] # return a part beggining with '(ROOT{...'
    s = s.partition(' ||| ')[0] # ONLY TEMPORARILY!!!
    #s = '(ROOT{0-15} ([S]{0-14} ([S]{0-6} ([X]{0-6} rozporzdzenie ([X]{2-5} ( WE )) nr)) ([X]{6-14} 1172 / 95 wprowadza si� nast�puj�ce zmiany :)))'
    s = s + '-#end#-'
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
            node =  Node()  # create new node
            oldnode.addChild(node) # create a connection between old node and his son # DEBUG ---WHY DOES NOT FUNCTION???
            # parent
            node.parent = oldnode # create a connection between new node and his father
            node.parentD = '['+oldnode.sClass+']{'+str(oldnode.iFrom)+'-'+str(oldnode.iTo)+'}' # DEBUG
            num = num + 1 # DEBUG
            node_no.append(num) # DEBUG
            print "child" , len ( oldnode.getChildren())
                
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
            sText = s[i:].partition('}')[2].partition(' ([')[0]
            if sText.count(')') == 0 and sText != '': 
                node.sString = node.sString + rplBrackets(sText)
                node.sChildrenD = node.sChildrenD +'<<>>'+rplBrackets(sText) # DEBUG
            # lChildren

        if s[i] == ')': # if closing bracket
            # sString --> between } and ) or between next to last ) and last )
            sText = rplBrackets(s[:i].rpartition('}')[2].split(')')[-1])
            if sText != '':
                node.sString = node.sString + sText
                node.sChildrenD = node.sChildrenD +'<<>>'+sText # DEBUG
            # sChildrenD
            node.sChildrenD = node.sChildrenD.strip('<<>>').split('<<>>') # DEBUG
            
            key = '['+node.sClass+']{'+str(node.iFrom)+'-'+str(node.iTo)+'}' # DEBUG
            data[key] = [node_no[-1],key,node.sClass,node.iFrom,node.iTo,node.parentD,node.sChildrenD,node.sString] # DEBUG
            node = node.parent # parent node become (active) node
            node_no.pop() # DEBUG

    #print 'node number,key,class,from,to,parent,children,string' # DEBUG
    for key in data:
        #print data[key],'\n'
        pass

    # find children of ROOT
    snt = ''
    for item in data:
        if data[item][1].count('[ROOT]'):
            for child in data[item][6]:
                snt = snt + child
                break

    # create an original sentence
    a = 0
    while re.findall('[[].[]][{]\d+-\d+[}]',snt) != [] and a < 1000:
        for item in re.findall('[[].[]][{]\d+-\d+[}]',snt):
            snt = snt.replace(item,getStr(data[item][6]))
            break
        a = a + 1
    if a == 1000: print '>1000 operations in creating sentence!'
    output = output+snt.strip(' ')+'\n'

    # iteration menu:
    if line_no % 100 == 0: print line_no
    if line_no == 10000:
        print '>10000 lines in file!'
        break

# print output
g = open('output','w')
g.write(output)
g.close()
