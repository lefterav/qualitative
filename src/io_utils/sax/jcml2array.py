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
    def __init__(self, globalAtts, srcAtts, tgtAtts, refAtts, className):
        self.discrete = {}
        self.TAG_DOC = 'jcml'
        self.TAG_SENT = 'judgedsentence'
        self.TAG_SRC = 'src'
        self.TAG_TGT = 'tgt'
        self.TAG_REF = 'ref'
        noOfXColumns = len(globalAtts)+len(srcAtts)+len(tgtAtts)+len(refAtts)
        self.x = zeros((noOfXColumns))
        self.y = zeros((1))
        self.allAttsCheck = set(set(globalAtts) | set(srcAtts) | set(tgtAtts) \
                                | set(refAtts) | set(className))
        self.allAttsCheckSet = set()
        self.actualSentId = 0
        
    
    '''
    Call conversion function and return matrices.
    @param returnDict: boolean value, if a string dictionary should be 
    returned (True) or not (False) 
    @return x, y: numpy matrices X (attribute values) and Y (class names)
    @return discrete: a dictionary with assigned numerical substitutions
    of string values that were parsed from jcml file
    '''
    def get_array(self, returnDict, jcmlFile):
        self.convert_jcml_attributes(globalAtts, srcAtts, tgtAtts, refAtts, \
                                     className, jcmlFile)
        if returnDict: return self.x, self.y, self.discrete
        else: return self.x, self.y
    
    
    '''
    Parse jcml file and convert parsed values into numpy matrix X (attribute
    values) and Y (class names).
    @param globalAtts: list of global attributes to be parsed in jcml file
    @param sourceAtts: list of source attributes to be parsed in jcml file
    @param targetAtts: list of target attributes to be parsed in jcml file
    @param referenceAtts: list of reference attributes to be parsed in jcml file
    @param className: class name to be parsed in jcml file
    @param jcmlFile: jcml filename
    '''
    def convert_jcml_attributes(self, globalAtts, srcAtts, tgtAtts, refAtts, \
                                className, jcmlFile):
        sourceFile = open(jcmlFile, "r")
        # get an iterable
        context = iterparse(sourceFile, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        
        globalRow = []
        srcRow = []
        tgtRows = []
        refRow = []
        for event, elem in context:
            if event == "start" and elem.tag == self.TAG_SENT:
                self.actualSentId = elem.attrib.get('id')
                for attr in globalAtts:
                    globalRow.append(self.encode_str(elem.attrib.get(attr), \
                                                     attr))
                    
            elif event == "start" and elem.tag == self.TAG_SRC:
                for attr in srcAtts:
                    srcRow.append(self.encode_str(elem.attrib.get(attr), attr))
            elif event == "start" and elem.tag == self.TAG_TGT:
                tgtRow = []
                for attr in tgtAtts:
                    tgtRow.append(self.encode_str(elem.attrib.get(attr), attr))
                tgtRows.append(tgtRow)
                for attr in className:
                    self.y = vstack((self.y, self.encode_str(elem.attrib.get \
                                                             (attr), attr)))
            
            elif event == "start" and elem.tag == self.TAG_REF:
                for attr in refAtts:
                    refRow.append(self.code_str(elem.attrib.get(attr), attr))
            
            elif event == "end" and elem.tag == self.TAG_SENT:
                
                for tgtRow in tgtRows:
                    # summarize the whole row of X matrix
                    row = []
                    row.extend(globalRow)
                    row.extend(srcRow)
                    row.extend(tgtRow)
                    row.extend(refRow)                        

                    # check if all attributes were found in jcml sentence
                    notFoundAtts = self.allAttsCheck - self.allAttsCheckSet
                    if notFoundAtts:
                        sys.exit("Following attributes weren't found: %s\nSentence id: %s" \
                                 % (notFoundAtts, self.actualSentId))

                    # insert row into X matrix
                    self.x = vstack((self.x, row))
                
                # delete content of previous rows (previous sentence)
                globalRow = []
                srcRow = []
                refRow = []
            root.clear()       
                
        # delete first rows in matrices (left from matrix initialization)
        self.x = delete(self.x, 0, 0)
        self.y = delete(self.y, 0, 0)

    
    '''
    If elem is not a float, assign a unique number to a string that occurred
    in matrix X. Matrix X contains attribute values.
    Strings with an assigned numbers are saved into a dictionary.
    @param elem: attribute value gained from jcml file.
    @param attr: attribute name
    @return: assigned unique number
    '''
    def encode_str(self, elem, attr):
        # add attr to the check set
        self.allAttsCheckSet.add(attr)
        
        # if elem is a number, return float
        try:
            return float(elem)
        # if elem is not a number, convert elem to string and assign a value
        except:
            if elem == None:
                sys.exit('Attribute %s has a None value!\nSentence id: %s' \
                         % (attr, self.actualSentId))
            s = str(elem)
            if attr in self.discrete.keys():
                if elem in self.discrete[attr].keys():
                    # return assigned int value
                    return self.discrete[attr][elem]
                else:
                    # assign a number greater by 1 than the actual greatest one
                    elemNo = 0
                    for key, value in self.discrete[attr].items():
                        if elemNo < value: elemNo = value
                    elemNo += 1
                    self.discrete[attr].update({elem:elemNo})
                    # return assigned int value
                    return self.discrete[attr][elem]
            else:
                self.discrete[attr] = {elem:0}
                # return assigned int value (always 0 in this case)
                return self.discrete[attr][elem]
                

if __name__ == '__main__':
    # command line arguments definition
    parser = OptionParser()
    parser.add_option("-g", '--globalAtts', dest='globalAtts', \
    help="global attributes to be extracted, multiple parameters are separated by comma")
    parser.add_option("-s", '--srcAtts', dest='srcAtts', \
    help="source attributes to be extracted, multiple parameters are separated by comma")
    parser.add_option("-t", '--tgtAtts', dest='tgtAtts', \
    help="target attributes to be extracted, multiple parameters are separated by comma")
    parser.add_option("-r", '--refAtts', dest='refAtts', \
    help="reference attributes to be extracted, multiple parameters are separated by comma")
    parser.add_option("-c", '--className', dest='className', \
    help="class name, it can be only 1 parameter!")
    parser.add_option("-f", '--jcmlFile', dest='jcmlFile', \
    help="path to jcml file")
    parser.add_option("-d", "--returnDict", dest="returnDict", default=False, \
    help="return dictionary with numerical string assignments (default False), for True type 'True' or '1'")
    
    # command line arguments check
    opt, args  = parser.parse_args()
    if not opt.jcmlFile: sys.exit('ERROR: Option --jcmlFilename is missing!')
    #if not opt.globalAtts: sys.exit('ERROR: Option --global attributes are missing!')
    #if not opt.srcAtts: sys.exit('ERROR: Option --source attributes are missing!')
    #if not opt.tgtAtts: sys.exit('ERROR: Option --target attributes are missing!')
    #if not opt.refAtts: sys.exit('ERROR: Option --reference attributes are missing!')
    #if not opt.className: sys.exit('ERROR: Option --class name is missing!')
    #if not opt.returnDict: sys.exit('ERROR: Option --return dictionary is missing!')
    if opt.globalAtts: globalAtts = opt.globalAtts.split(',')
    else: globalAtts = []
    if opt.srcAtts: srcAtts = opt.srcAtts.split(',')
    else: srcAtts = []
    if opt.tgtAtts: tgtAtts = opt.tgtAtts.split(',')
    else: tgtAtts = []
    if opt.refAtts: refAtts = opt.refAtts.split(',')
    else: refAtts = []
    if opt.className: className = [opt.className]
    else: className = []
    Jcml2Array(globalAtts, srcAtts, tgtAtts, refAtts, className, \
               opt.jcmlFile).get_array(opt.returnDict)
