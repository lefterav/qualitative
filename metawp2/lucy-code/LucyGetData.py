import codecs
import os
import re
import sys
import traceback
from LucyTrees import BaseTree


class LucyGetData():
    def __init__(self):
        filename = sys.argv[1]
        self.sentenceSeparator = '#sentence-separator#'

        data = self.convert_lucy_file(filename)
        self.get_attributes(data)


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
    """
    def get_attributes(self, data):

        for part in self.get_parts(data):
            trees = re.split(self.sentenceSeparator, part)[1:]

            for i in range(len(trees)):
                print 'Tree No.: %s, Tree char length: %s' % (str(i), len(trees[i]))
                bt = BaseTree(trees[i], {}, '')                                      
                print bt.dct, '\n\n'


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
        print '%s converted successfully' % filename
        return data


LucyGetData()
