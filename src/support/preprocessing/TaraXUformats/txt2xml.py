'''
Created on Jan 24, 2012

@author: jogin


The script converts line-by-line sentences from txt file to xml format.

Example for command line:
--lang english
--srcFilename /media/DATA/Arbeit/DFKI/120123_txt2xml/nc11/source.txt
--tgtFilename /media/DATA/Arbeit/DFKI/120123_txt2xml/nc11/source2.xml
--setid iwslt11_tst2011
--setType source
--sysid system3
'''

import sys
from optparse import OptionParser

parser = OptionParser()

parser.add_option("-s", '--srcFilename', dest='srcFilename', \
                        help="source txt filename with line-by-line sentences")
parser.add_option("-x", '--tgtFilename', dest='tgtFilename', \
                                                    help="target xml filename")
parser.add_option("-i", '--setid', dest='setid', help="id of the sentence set")
parser.add_option("-t", '--setType', dest='setType', \
                              help="type of sentence set (source/translation)")
parser.add_option("-l", '--lang', dest='lang', \
                                      help="language of source file sentences")
parser.add_option("-l", '--sysid', dest='sysid', \
                                                help="translation system name")

options, args  = parser.parse_args()
if not options.srcFilename: sys.exit('Option --srcFilename is missing!')
if not options.tgtFilename: sys.exit('Option --tgtFilename is missing!')
if not options.setid: sys.exit('Option --setid is missing!')
if not options.setType: sys.exit('Option --setType is missing!')
if not options.lang: sys.exit('Option --lang is missing.')
if not options.sysid: sys.exit('Option --sysid is missing.')

srcFilename = options.srcFilename
tgtFilename = options.tgtFilename
setid = options.setid
setType = options.setType
lang = options.lang
sysid = options.sysid

f = open(srcFilename)
content = f.read().strip()
f.close()

sentences = content.split('\n')

output = '<?xml version="1.0" encoding="UTF-8"?>\n'
output += '<set setid="%s" type="%s" lang="%s" sysid="%s">\n' \
                                                % (setid, setType, lang, sysid)
for i in range(len(sentences)):
    output += '\t<seg docid="%s" id="%s">\n' % (setid, i+1)
    output += '\t\t%s\n' % sentences[i]
    output += '\t</seg>\n'
output += '</set>\n'

f = open(tgtFilename, 'w')
f.write(output)
f.close()

print '%s was generated' % tgtFilename
