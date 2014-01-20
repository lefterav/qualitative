import codecs
import os
import re
import sys
import traceback
from LucyTrees import BaseTree


"""
This class converts new 'XML' lucy format into old 'bracket' format.
After that various attributes from each sentence are extracted.
"""
class LucyGetData():
    def __init__(self):
        filenameInput = sys.argv[1]
        filenameOutput = sys.argv[2]
        self.sentenceSeparator = '#sentence-separator#'

        data = self.convert_lucy_file(filenameInput)
        self.get_attributes(data, filenameOutput)


    """
    This function splits the lucy file to analysis, transfer and generation part.
    @param data: string
    @return: list with 3 lucy file parts
    """
    def get_parts(self, data):
        analysis = data.split('<analysis>')[1].split('</analysis>')[0]
        transfer = data.split('<transfer>')[1].split('</transfer>')[0]
        generation = data.split('<generation>')[1].split('</generation>')[0]
        return [analysis, transfer, generation]


    """
    This function returns for each sentence in lucy file a dictionary with parsed parameters.
    @param data: list with analysis, transfer and generation part (string)
    @param outFile: output filename where the dictionary will be saved as strings for manual check (string)
    """
    def get_attributes(self, data, outFilename):
        
        outFile = codecs.open(outFilename, 'w', 'utf-8')
        for part in self.get_parts(data):
            trees = re.split(self.sentenceSeparator, part)[1:]

            for i in range(len(trees)):
                treeInfo = '\n\n\n\nTree No %s, tree char length %s:\n\n' % (str(i), len(trees[i]))
                outFile.write(treeInfo); print treeInfo
                bt = BaseTree(trees[i], {}, '')
                outFile.write(str(bt.dct))
                bt.dct = {}
        outFile.close()


    """
    This function converts new lucy format into the old one.
    @param data: new lucy format (XML)
    @return: old lucy format with round brackets
    """
    def convert_lucy_file(self, filename):
        data = codecs.open(filename, 'r', 'utf-8').read()
        data = re.sub('<NODE><SENTENCE>[^<]*</SENTENCE>', '\n%s(\n' % (self.sentenceSeparator), data)
        data = data.replace('<NODE>', '(')
        data = data.replace('</NODE>', ')')
        data = data.replace('<CAT>S</CAT>', '(CAT S)')
        data = data.replace('<ALO>', 'ALO ')
        data = data.replace('</ALO>', ' ')
        data = data.replace('<CAT>', 'CAT ')
        data = data.replace('</CAT>', ' ')
        data = data.replace('<CAN>', 'CAN ')
        data = data.replace('</CAN>', ' ')
        data = data.replace(' )', ')')
        leftBracketCAN = re.search('CAN ("[^"]*\([^"]*")', data)
        if leftBracketCAN: data = data.replace(leftBracketCAN.group(1), leftBracketCAN.group(1).replace('(', '<left-round-bracket>'))
        leftBracketALO = re.search('ALO ("[^"]*\([^"]*")', data)
        if leftBracketALO: data = data.replace(leftBracketALO.group(1), leftBracketALO.group(1).replace('(', '<left-round-bracket>'))
        rightBracketCAN = re.search('CAN ("[^"]*\)[^"]*")', data)
        if rightBracketCAN: data = data.replace(rightBracketCAN.group(1), rightBracketCAN.group(1).replace(')', '<right-round-bracket>'))
        rightBracketALO = re.search('ALO ("[^"]*\)[^"]*")', data)
        if rightBracketALO: data = data.replace(rightBracketALO.group(1), rightBracketALO.group(1).replace(')', '<right-round-bracket>'))
        print '%s converted successfully' % filename
        return data


LucyGetData()
#print re.search('CAN ("[^"]*\([^"]*")', 'CAN "("').group(1)
