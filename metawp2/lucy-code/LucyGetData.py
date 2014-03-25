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
        self.sentenceSeparator = '#sentence-separator#'


    """
    This function splits the lucy file to analysis, transfer and generation part.
    @param data: lucy tree file (string)
    @return: analysis, transfer and generation part of lucy tree file (list)
    """
    def get_parts(self, data):
        analysis = data.split('<analysis>')[1].split('</analysis>')[0]
        transfer = data.split('<transfer>')[1].split('</transfer>')[0]
        generation = data.split('<generation>')[1].split('</generation>')[0]
        return [analysis, transfer, generation]


    """
    This function returns for each sentence in lucy file a dictionary with parsed parameters.
    @param data: old bracket lucy tree format (string)
    @param outFile: output filename where the dictionary will be saved as strings for manual check (string)
    """
    def process_old_format_file(self, data, outFilename):
        
        outFile = codecs.open(outFilename, 'w', 'utf-8')
        
        # analysis, transfer and generation part
        for part in self.get_parts(data):
            trees = re.split(self.sentenceSeparator, part)[1:]

            for i in range(len(trees)):
                treeInfo = '\n\n\n\nTree No %s, tree char length %s:\n\n' % (str(i), len(trees[i]))
                outFile.write(treeInfo); print treeInfo
                sentenceFeatures = self.process_sentence(trees[i])
                outFile.write(str(sentenceFeatures))
        outFile.close()


    """
    This function calls BaseTreee class, where tree features are parsed and saved as dict.
    @param sentence: Lucy sentence in old bracket format (string)
    @return: dictionary with parsed features (dict)
    """
    def process_sentence(self, sentence):
        bt = BaseTree(sentence, {}, '')
        return bt.dct
        

    """
    This function converts new lucy format into the old one.
    @param data: new lucy XML format (string)
    @return: old lucy format with round brackets (string)
    """
    def process_new_format_file(self, filename):
        data = codecs.open(filename, 'r', 'utf-8').read() # remove from here (1 sentence per time)
        # 1 sentence per time, but from bracket format (old one)
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


if __name__ == '__main__':
    filenameInput = sys.argv[1] # path to file with XML lucy format
    filenameOutput = sys.argv[2] # path where a dict with trees features will be saved as string

    objLucy = LucyGetData()
    data = objLucy.process_new_format_file(filenameInput)
    objLucy.process_old_format_file(data, filenameOutput)

