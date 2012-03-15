#!/usr/bin/env python2

'''
Created on Jan 30, 2012

@author: jogin


The script converts sgm xml format to another xml format.

Example for command line:
--linksFile r2-testset.en-de.links.noEmpty
--srcFile r2-testset.en-de.en.noEmpty
--refFile r2-testset.en-de.de.noEmpty
--srcLang en
--tgtLang de
--setid my-set-id
--combxml combined.en-de.xml
--sys1File moses.en-de.txt
--sys1Name moses

There can be up to 5 sys parameters (maximum is sys5File, sys5Name).
'''

import sys
from optparse import OptionParser

def escapeXML(string):
    return string.replace("<", "&lt;").replace(">", "&gt;")

# command line arguments definition
parser = OptionParser()
parser.add_option("-l", '--linksFile', dest='linksFile', \
                help="links txt file with line-by-line sentence id and doc id")
parser.add_option("-s", '--srcFile', dest='srcFile', \
                            help="source txt file with line-by-line sentences")
parser.add_option("-r", '--refFile', dest='refFile', \
                         help="reference txt file with line-by-line sentences")
parser.add_option("-g", '--srcLang', dest='srcLang', help="source language")
parser.add_option("-t", '--tgtLang', dest='tgtLang', help="target language")
parser.add_option("-i", '--setid', dest='setid', help="id of the whole set")
parser.add_option("-x", '--combxml', dest='combxml', \
                                       help="name of output combined xml file")

# optional command line arguments
parser.add_option("-1", '--sys1File', dest='sys1File', \
                   help="1.system output txt file with line-by-line sentences")
parser.add_option("-a", '--sys1Name', dest='sys1Name', help="1.system name")
parser.add_option("-2", '--sys2File', dest='sys2File', \
                   help="2.system output txt file with line-by-line sentences")
parser.add_option("-b", '--sys2Name', dest='sys2Name', help="2.system name")
parser.add_option("-3", '--sys3File', dest='sys3File', \
                   help="3.system output txt file with line-by-line sentences")
parser.add_option("-c", '--sys3Name', dest='sys3Name', help="3.system name")
parser.add_option("-4", '--sys4File', dest='sys4File', \
                   help="4.system output txt file with line-by-line sentences")
parser.add_option("-d", '--sys4Name', dest='sys4Name', help="4.system name")
parser.add_option("-5", '--sys5File', dest='sys5File', \
                   help="5.system output txt file with line-by-line sentences")
parser.add_option("-e", '--sys5Name', dest='sys5Name', help="5.system name")

# check of command line arguments
options, args  = parser.parse_args()
if not options.linksFile: sys.exit('ERROR: Option --linksFile is missing!')
if not options.srcFile: sys.exit('ERROR: Option --srcFile is missing!')
#if not options.refFile: sys.exit('ERROR: Option --refFile is missing!')
if not options.srcLang: sys.exit('ERROR: Option --srcLang is missing!')
if not options.tgtLang: sys.exit('ERROR: Option --tgtLang is missing!')
if not options.setid: sys.exit('ERROR: Option --setid is missing!')
#if not options.combxml: sys.exit('ERROR: Option --combxml is missing!')

# variables with command line arguments
linksFile = options.linksFile
srcFile = options.srcFile
refFile = options.refFile
srcLang = options.srcLang
tgtLang = options.tgtLang
setid = options.setid
combxml = options.combxml

# read input files
f = open(linksFile)
contentLinks = f.read().strip().split('\n')
f.close()

f = open(srcFile)
contentSrc = f.read().strip().split('\n')
f.close()

if refFile:
    f = open(refFile)
    contentRef = f.read().strip().split('\n')
    f.close()
else:
    contentRef = None

# read input system files if exist
contentSys1 = []
sys1Name = ''
contentSys2 = []
sys2Name = ''
contentSys3 = []
sys3Name = ''
contentSys4 = []
sys4Name = ''
contentSys5 = []
sys5Name = ''

if options.sys1File and options.sys1Name:
    f = open(options.sys1File)
    contentSys1 = f.read().strip().split('\n')
    f.close()
    sys1Name = options.sys1Name
    
if options.sys2File and options.sys2Name:
    f = open(options.sys2File)
    contentSys2 = f.read().strip().split('\n')
    f.close()
    sys2Name = options.sys2Name

if options.sys3File and options.sys3Name:
    f = open(options.sys3File)
    contentSys3 = f.read().strip().split('\n')
    f.close()
    sys3Name = options.sys3Name

if options.sys4File and options.sys4Name:
    f = open(options.sys4File)
    contentSys4 = f.read().strip().split('\n')
    f.close()
    sys4Name = options.sys4Name

if options.sys5File and options.sys5Name:
    f = open(options.sys5File)
    contentSys5 = f.read().strip().split('\n')
    f.close()
    sys5Name = options.sys5Name

# check if number of lines in input files is equal
if len(contentLinks) != len(contentSrc):
    sys.exit('ERROR: Number of lines in linksFile and srcFile not equal!')
if contentRef and len(contentLinks) != len(contentRef):
    sys.exit('ERROR: Number of lines in linksFile and refFile not equal!')
if contentSys1 and len(contentLinks) != len(contentSys1):
    sys.exit('ERROR: Number of lines in linksFile and sys1File not equal!')
if contentSys2 and len(contentLinks) != len(contentSys2):
    sys.exit('ERROR: Number of lines in linksFile and sys2File not equal!')
if contentSys3 and len(contentLinks) != len(contentSys3):
    sys.exit('ERROR: Number of lines in linksFile and sys3File not equal!')
if contentSys4 and len(contentLinks) != len(contentSys4):
    sys.exit('ERROR: Number of lines in linksFile and sys4File not equal!')
if contentSys5 and len(contentLinks) != len(contentSys5):
    sys.exit('ERROR: Number of lines in linksFile and sys5File not equal!')

# create combined xml file
output = '<?xml version="1.0" encoding="UTF-8"?>\n'
output += '<set setid="%s" source-language="%s" target-language="%s">\n' \
                                                    % (setid, srcLang, tgtLang)

for i in range(len(contentLinks)):
    if len(contentLinks[i].split('\t'))==3:
        segid = contentLinks[i].split('\t')[1]
        docid = contentLinks[i].split('\t')[2]
    elif len(contentLinks[i].split('\t'))==2:
        segid = contentLinks[i].split('\t')[0]
        docid = contentLinks[i].split('\t')[1]
    source = contentSrc[i]
    if contentRef:
        reference = contentRef[i]
    else:
        reference = None
    
    output += '\t<seg id="%s" docid="%s">\n' % (segid, docid)
    output += '\t\t<source>%s</source>\n' % escapeXML(source)
    if reference:
        output += '\t\t<reference>%s</reference>\n' % escapeXML(reference)
    if contentSys1: output +='\t\t<translation system="%s">%s</translation>\n'\
                                                   % (sys1Name, escapeXML(contentSys1[i]))
    if contentSys2: output +='\t\t<translation system="%s">%s</translation>\n'\
                                                   % (sys2Name, escapeXML(contentSys2[i]))
    if contentSys3: output +='\t\t<translation system="%s">%s</translation>\n'\
                                                   % (sys3Name, escapeXML(contentSys3[i]))
    if contentSys4: output +='\t\t<translation system="%s">%s</translation>\n'\
                                                   % (sys4Name, escapeXML(contentSys4[i]))
    if contentSys5: output +='\t\t<translation system="%s">%s</translation>\n'\
                                                   % (sys5Name, escapeXML(contentSys5[i]))
    output += '\t</seg>\n'
output += '</set>\n'

if combxml:
    f = open(combxml, 'w')
    f.write(output)
    f.close()
    print '%s was generated' % combxml
else:
    sys.stdout.write(output)

