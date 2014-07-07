'''
Created on 7 Jul 2014

@author: Eleftherios Avramidis
'''

from ml.lib.orange import OrangeRuntimeRanker 
from io_utils.sax.cejcml import CEJcmlReader 
from collections import OrderedDict
import sys

if __name__ == '__main__':
    classifiername = sys.argv[1]
    ranker = OrangeRuntimeRanker(classifiername)

    jcmlfilename = sys.argv[2]
    for parallelsentence in CEJcmlReader(jcmlfilename).get_parallelsentences():
        ranking, description = ranker.rank_sentence(parallelsentence)
        ranking_dict = OrderedDict(ranking)
        selected_sentence = ranking_dict[1] 
        print selected_sentence.get_string()
            