'''
Created on Aug 31, 2011

@author: elav01
'''

from saxprocessor import SaxProcessor
from io.dataformat.jcmlformat import JcmlFormat

class SaxJcmlProcessor(SaxProcessor):
    '''
    classdocs
    '''
    inputformat = JcmlFormat
    outputformat = JcmlFormat


    
        