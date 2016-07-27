'''
Created on 31 Oct 2013

@author: Eleftherios Avramidis
'''

from xml.etree.cElementTree import iterparse
import sys
from dataprocessor.input.jcmlreader import JcmlReader

if __name__ == '__main__':
    source_file = open(sys.argv[1], "r")
    # get an iterable
    context = iterparse(source_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    
    attributes = []
    target_id = 0
    for event, elem in context:
        #new sentence: get attributes
        if event == "start" and elem.tag == "ref":
            print elem.text
        