'''
Created on Apr 2, 2012

@author: jogin
'''

from optparse import OptionParser
import re
import sys
import time


"""
This class reads txt file with translation system analysis and saves as
much information as possible to a dictionary.
"""
class ReadSystemAnalysis:
    """
    @param filename: Name of input file with translation system analysis.
    @type filename: string 
    """
    def __init__(self, filename):
        start = time.time()
        self.att = {}
        f = file(filename)
        lineNo = 0
        partNo = 0
        end = False
        while 1:
            transPart = ''
            tempTransPart = ''
            line = f.readline()
            lineNo = lineNo + 1
            while not line.startswith('Finished translating\n'):
                line = f.readline()
                lineNo = lineNo + 1
                tempTransPart = '%s%s' % (tempTransPart, line)
                if lineNo % 3000 == 0:
                    transPart = '%s%s' % (transPart, tempTransPart)
                    tempTransPart = 0
                print lineNo
                
                # if file ends
                if not line:
                    f.close()
                    #f = file('%s_dict' % filename, 'w')
                    #f.write(str(self.att))
                    #f.close()
                    print time.time()-start
                    sys.exit()
                    
            transPart = '%s%s' % (transPart, tempTransPart)
            if not end:
                print 'parsing...'
                partNo += 1
                self.add_attributes(transPart, partNo)
            #time.sleep(4)

    
    """
    This function adds attributes to global dictionary. These attributes are
    parsed from 1 line of translation system analysis. 
    @param transPart: translation system analysis for 1 line (1 sentence)
    @type transPart: string
    @param partNo: number of translation system part
    @type partNo: int 
    """
    def add_attributes(self, transPart, partNo):
        print time.time()
        # get 'Total translation options'
        toTrOp = re.search('Total translation options: (\d+)\n', transPart).group(1)
        self.att['total_transl_options', partNo] = toTrOp
        
        # get 'Total translation options pruned'
        toTrOpPr = re.search('Total translation options pruned: (\d+)\n', transPart).group(1)
        self.att['total_transl_options_pruned', partNo] = toTrOpPr
        
        # get 'translation options spanning'
        for item in re.findall('translation options spanning from  (\d+) to (\d+) is (\f+)\n', transPart):
            self.att['transl_options_spanning', partNo, item[0], item[1]] = item[2]
        
        # get 'future cost'
        for item in re.findall('future cost from (\d+) to (\d+) is ([-.\d]+)\n', transPart):
            self.att['future_cost', partNo, item[0], item[1]] = item[2]
        
        print time.time()


# check command line arguments
parser = OptionParser()
parser.add_option("-f", '--filename', dest='filename', \
                    help="Name of input file with translation system analysis")
options, args  = parser.parse_args()
#if not options.filename: sys.exit('ERROR: Option --filename is missing!')
filename = '/media/DATA/Arbeit/DFKI/120402_sentence_analysis/SERVICE_EXCELLENCE_cust_euDE_4.txt.log'
ReadSystemAnalysis(options.filename)