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

import random
import sys
from optparse import OptionParser

def escapeXML(string):
        # Some file were already converted to "XML format", so first we convert them back
            return string.replace("&lt;", "<").replace("&gt;",">").replace("&", "&amp;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;")

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
parser.add_option("-b", "--block-size", dest="blockSize", type=int, default=100,
                                       help="block size for repetitions")

# optional command line arguments
parser.add_option("-f", '--sysFiles', dest='sysFiles', \
        help="system output txt files with line-by-line sentences (':' separated list)")
parser.add_option("-n", '--sysNames', dest='sysNames', help="system name (':' separated list)")

# check of command line arguments
options, args  = parser.parse_args()
if not options.linksFile: sys.exit('ERROR: Option --linksFile is missing!')
if not options.srcFile: sys.exit('ERROR: Option --srcFile is missing!')
if not options.srcLang: sys.exit('ERROR: Option --srcLang is missing!')
if not options.tgtLang: sys.exit('ERROR: Option --tgtLang is missing!')
if not options.setid: sys.exit('ERROR: Option --setid is missing!')

# read input files
f = open(options.linksFile)
contentLinks = f.read().strip().split('\n')
f.close()

f = open(options.srcFile)
contentSrc = f.read().strip().split('\n')
f.close()

if options.refFile:
    f = open(options.refFile)
    contentRef = f.read().strip().split('\n')
    f.close()
else:
    contentRef = None

sysFnames = options.sysFiles.split(":")
sysContents = []
lContentLinks = len(contentLinks)
for fname in sysFnames:
    f = open(fname)
    content = f.read().strip().split('\n')
    f.close()
    if len(content) != lContentLinks:
        sys.exit('ERROR: Number of lines in linksFile and %s not equal!' % fname)
    sysContents.append(content)
sysNames = options.sysNames.split(":")
nSystems = len(sysNames)

# Determine the (random) order of the systems
systemsOrder = []
for i in range(len(contentLinks)):
    thisOrder = range(nSystems)
    random.shuffle(thisOrder)
    systemsOrder.append(thisOrder)

# create combined xml file
output = '<?xml version="1.0" encoding="UTF-8"?>\n'
output += '<set id="%s" source-language="%s" target-language="%s">\n' \
                                                    % (options.setid, options.srcLang, options.tgtLang)

beginCurrentBlock = 0
endCurrentBlock = options.blockSize
while beginCurrentBlock < len(contentLinks):
    for run in range(nSystems):
        for i in xrange(beginCurrentBlock, min(endCurrentBlock, len(contentLinks))):
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
            
            fullsegid = "%s-%s-%s" % (options.setid, docid, segid)

            output += '\t<seg id="%s" doc-id="%s">\n' % (fullsegid, docid)
            output += '\t\t<source>%s</source>\n' % escapeXML(source)
            if reference:
                output += '\t\t<reference>%s</reference>\n' % escapeXML(reference)
            output += '\t\t<translation system="%s">%s</translation>\n'\
                                                       % (sysNames[systemsOrder[i][run]], escapeXML(sysContents[run][i]))
            output += '\t</seg>\n'
    beginCurrentBlock = endCurrentBlock
    endCurrentBlock += options.blockSize
output += '</set>\n'

if options.combxml:
    f = open(options.combxml, 'w')
    f.write(output)
    f.close()
    print '%s was generated' % options.combxml
else:
    sys.stdout.write(output)

