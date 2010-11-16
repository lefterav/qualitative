#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Created on 15 Οκτ 2010

@author: elav01
'''

from io.input.xmlreader import XmlReader
from io.input.orangereader import OrangeData


if __name__ == '__main__':
    
    pdr = XmlReader("/home/elav01/workspace/TaraXUscripts/data/evaluations_feat.jcml") 
    print pdr.getAttributes()
    print pdr.getParallelSentences()
    ds =  pdr.getDataSet()
    orange = OrangeData(ds)