'''
Created on 31 Oct 2013

@author: Eleftherios Avramidis
'''

from xml.etree.cElementTree import iterparse
import sys
from dataprocessor.input.jcmlreader import JcmlReader
import codecs


try:
    TAG = sys.argv[3]
except:
    TAG = 'ref'

if __name__ == '__main__':
    source_file = open(sys.argv[1], "r")
    # get an iterable
    context = iterparse(source_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()

    filename_output = sys.argv[2]
    file_output = codecs.open(filename_output, 'w', 'utf-8') 

    attributes = []
    target_id = 0
    for event, elem in context:
        #new sentence: get attributes
        if event == "start" and elem.tag == TAG:
            #try:
            print >>file_output, elem.text
            #except:
            #    print unicode(elem.text)
        
