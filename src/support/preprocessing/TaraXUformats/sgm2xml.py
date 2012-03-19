#!/usr/bin/env python2
'''
Created on Jan 25, 2012

@author: jogin


The script converts sgm xml format to another xml format.

Example for command line:
--srcFilename /media/DATA/Arbeit/DFKI/120125_sgm2xml/newstest2009.detokenized.sgm.4
--tgtFilename /media/DATA/Arbeit/DFKI/120125_sgm2xml/newstest2009.detokenized.sgm.4.xml
--setType source
'''

import re
import sys
from optparse import OptionParser

parser = OptionParser()

parser.add_option("-s", '--srcFilename', dest='srcFilename', \
                        help="source txt filename with line-by-line sentences")
parser.add_option("-x", '--tgtFilename', dest='tgtFilename', \
                                                    help="target xml filename")
parser.add_option("-t", '--setType', dest='setType', \
                              help="type of sentence set (source/translation)")

options, args  = parser.parse_args()
if not options.srcFilename: sys.exit('ERROR: Option --srcFilename is missing!')
if not options.tgtFilename: sys.exit('ERROR: Option --tgtFilename is missing!')
if not options.setType: print 'WARNING: Option --setType is missing!'

srcFilename = options.srcFilename
tgtFilename = options.tgtFilename
if options.setType: setType = options.setType
else: setType = ''

f = open(srcFilename)
content = f.read().strip()
f.close()

# get setid
setid = re.search('setid="([^"]*)"', content)
if setid: setid = setid.group(1)
else:
    setid = ''
    print "WARNING: Can't find setid in sgm file."

# get srcLang
srcLang = re.search('srclang="([^"]*)"', content)
if srcLang: srcLang = srcLang.group(1)
else:
    srcLang = ''
    print "WARNING: Can't find srcLang in sgm file."

# get tgtLang
tgtLang = re.search('trglang="([^"]*)"', content)
if tgtLang: tgtLang = tgtLang.group(1)
else:
    tgtLang = ''
    print "WARNING: Can't find tgtLang in sgm file."


output = '<?xml version="1.0" encoding="UTF-8"?>\n'
output += '<set setid="%s" type="%s" srcLang="%s" tgtLang="%s">\n' \
                                           % (setid, setType, srcLang, tgtLang)

docs = re.findall('<doc .*?</doc>', content, re.DOTALL | re.IGNORECASE)
for doc in docs:
    # get sysid
    sysid = re.search('sysid="([^"]*)"', doc)
    if sysid: sysid = sysid.group(1)
    else:
        sysid = ''
        print "WARNING: Can't find sysid in sgm file."
    
    # get docid
    docid = re.search('docid="([^"]*)"', doc)
    if docid: docid = docid.group(1)
    else:
        docid = ''
        print "WARNING: Can't find docid in sgm file."
    
    # rewrite segments with new arguments
    segments = re.findall('<seg .*?</seg>', doc, re.IGNORECASE | re.MULTILINE)
    for i in range(len(segments)):
        output += '\t<seg docid="%s" sysid="%s" id="%s">\n' \
                                                          % (docid, sysid, i+1)
        output += '\t\t%s\n' % re.sub('<.*?>', '', segments[i]).strip()
        output += '\t</seg>\n'
output += '</set>\n'

f = open(tgtFilename, 'w')
f.write(output)
f.close()

print '%s was generated' % tgtFilename
