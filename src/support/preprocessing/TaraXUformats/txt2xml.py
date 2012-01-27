'''
Created on Jan 24, 2012

@author: jogin


The script converts line-by-line sentences from txt file to xml format.

Example for command line:
--srcLang english
--tgtLang german
--srcFilename /TaraXUscripts/support/preprocessing/TaraXUformats/source.txt
--tgtFilename /TaraXUscripts/support/preprocessing/TaraXUformats/source2.xml
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
                                                   help="type of sentence set")
parser.add_option("-l", '--srcLang', dest='srcLang', \
               help="source language of translation set (Option not required)")
parser.add_option("-g", '--tgtLang', dest='tgtLang', \
               help="target language of translation set (Option not required)")
parser.add_option("-d", '--sysid', dest='sysid', \
                                                help="translation system name")

options, args  = parser.parse_args()
if not options.srcFilename: sys.exit('ERROR: Option --srcFilename is missing!')
if not options.tgtFilename: sys.exit('ERROR: Option --tgtFilename is missing!')
if not options.setid: sys.exit('ERROR: Option --setid is missing!')
if not options.setType: sys.exit('ERROR: Option --setType is missing!')
if not options.sysid: sys.exit('ERROR: Option --sysid is missing!')

srcFilename = options.srcFilename
tgtFilename = options.tgtFilename
setid = options.setid
setType = options.setType
sysid = options.sysid

srcLang = ''
if not options.srcLang: print 'WARNING: Option --srcLang is missing.'
else: srcLang = options.srcLang

tgtLang = ''
if not options.tgtLang: print 'WARNING: Option --tgtLang is missing.'
else: tgtLang = options.tgtLang


f = open(srcFilename)
content = f.read().strip()
f.close()

sentences = content.split('\n')

output = '<?xml version="1.0" encoding="UTF-8"?>\n'
output += '<set setid="%s" type="%s" srcLang="%s" tgtLang="%s">\n' \
                                    % (setid, setType, srcLang, tgtLang)
for i in range(len(sentences)):
    output += '\t<seg docid="1" sysid="%s" id="%s">\n' % (sysid, i+1)
    output += '\t\t%s\n' % sentences[i]
    output += '\t</seg>\n'
output += '</set>\n'

f = open(tgtFilename, 'w')
f.write(output)
f.close()

print '%s was generated' % tgtFilename
