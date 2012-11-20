'''
Created on Nov 13, 2012

@author: jogin
'''
from xml.etree.cElementTree import iterparse
from numpy import *
from optparse import OptionParser
import sys


'''
Convert jcml data format into numpy matrix of float values.
'''
class Jcml2Array():
    def __init__(self, params, jcmlFile):
        self.discreteX = {}
        self.discreteY = {}
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_DOC = 'jcml'
        self.stringCodeX = 0
        self.stringCodeY = 0
        
        x, y = self.convert_jcml_attributes(params, jcmlFile)
        print x
        print self.discreteX
        print y
        print self.discreteY

    
    '''
    Parse jcml file and convert parsed values into numpy matrix X (attribute
    values) and Y (names of tags).
    @param params: parameters to be parsed in jcml file (list of strings)
    @param jcmlFile: jcml filename
    @return x, y: created numpy matrices
    '''
    def convert_jcml_attributes(self, params, jcmlFile):
        sourceFile = open(jcmlFile, "r")
        # get an iterable
        context = iterparse(sourceFile, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        x = zeros((len(params)))
        y = zeros((1))
        for event, elem in context:
            # create new list
            row = []
            if event == "start" and elem.tag == self.TAG_SENT:
                for param in params:
                    row.append(self.code_strsX(elem.attrib.get(param)))
                x = vstack((x, row))
                y = vstack((y, self.code_strsY(elem.tag)))
            # get tgt values into a list
            elif event == "start" and elem.tag == self.TAG_SRC:
                for param in params:
                    row.append(self.code_strsX(elem.attrib.get(param)))
                x = vstack((x, row))
                y = vstack((y, self.code_strsY(elem.tag)))
            elif event == "start" and elem.tag == self.TAG_TGT:
                for param in params:
                    row.append(self.code_strsX(elem.attrib.get(param)))
                x = vstack((x, row))
                y = vstack((y, self.code_strsY(elem.tag)))
        
        # delete first rows (left from matrix initialization)
        x = delete(x, 0, 0)
        y = delete(y, 0, 0)
        return x, y

    
    '''
    If elem is not a float, assign a unique number to a string that occurred
    in matrix X. Matrix X contains attribute values.
    Strings with an assigned numbers are saved into a dictionary.
    @param elem: attribute value gained from jcml file.
    @return: assigned unique number
    '''
    def code_strsX(self, elem):
        try:
            return float(elem)
        except:
            s = str(elem)
            if s in self.discreteX.keys():
                return self.discreteX[s]
            else:
                self.discreteX[s] = self.stringCodeX
                self.stringCodeX += 1
                return self.discreteX[s]
    
    '''
    If elem is not a float, assign a unique number to a string that occurred
    in matrix Y. Matrix Y contains names of tags.
    Strings with an assigned numbers are saved into a dictionary.
    @param elem: attribute value gained from jcml file.
    @return: assigned unique number
    '''
    def code_strsY(self, elem):
        try:
            return float(elem)
        except:
            s = str(elem)
            if s in self.discreteY.keys():
                return self.discreteY[s]
            else:
                self.discreteY[s] = self.stringCodeY
                self.stringCodeY += 1
                return self.discreteY[s]
                

if __name__ == '__main__':
    # command line arguments definition
    parser = OptionParser()
    parser.add_option("-p", '--params', dest='params', \
    help="parameters to be extracted, multiple params are separated by comma")
    parser.add_option("-f", '--jcmlFile', dest='jcmlFile', \
    help="path to jcml file")
    
    # command line arguments check
    opt, args  = parser.parse_args()
    if not opt.params: sys.exit('ERROR: Option --params is missing!')
    if not opt.jcmlFile: sys.exit('ERROR: Option --jcmlFile is missing!')
    params = opt.params.split(',')
    Jcml2Array(params, opt.jcmlFile)
