#!/usr/bin/env python2

'''
Created on Jan 25, 2012

@author: jogin


This script join xml files to one xml file.
xml files are as parameters in command line.
Order of content in big xml file is given by the order of parameters.
'''

import re
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-t", '--tgtFile', dest='tgtFile', \
                                               help="target big xml file")
options, args  = parser.parse_args()
if not options.tgtFile: sys.exit('Option --tgtFile is missing!')

tgtFile = options.tgtFile

g = open(tgtFile, 'w+')
g.write('<?xml version="1.0" encoding="UTF-8"?>\n')
#g.write('<multiset>\n')
for (i, filename) in enumerate(args):
    f = open(filename)
    content = f.read().strip()
    f.close()
    
    # remove xml heading tags
    content = re.sub('<\?.*?\?>','',content)
    if i > 0:
        # remove the set tags
        content = re.sub('<set.*?>','',content)
    if i < len(args) - 1:
        # remove the /set
        content = re.sub('</set>','',content)
    
    # add one TAB alignment and write to output xml
    lines = content.split('\n')
    g.writelines(['\t%s\n' % line for line in lines])

#g.write('</multiset>\n')
g.close()

print '%s was created!' % tgtFile

