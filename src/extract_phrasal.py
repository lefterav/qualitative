# -*- coding: utf-8 -*-

import sys
import codecs

def extract_trees(lucy, out):
    for line in lucy:
    	result = False
        if 'PHR-S' in line:
            result = True
	out.write(str(result) + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s LUCY' % sys.argv[0]
    else:
        lucy = codecs.open(sys.argv[1], 'r', 'utf-8')
	out = codecs.open(sys.argv[1] + '.phrasal', 'w', 'utf-8')
	extract_trees(lucy, out)
	out.close()
