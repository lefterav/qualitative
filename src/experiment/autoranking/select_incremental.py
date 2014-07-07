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
    outputfile = open(sys.argv[3], 'w')
    counts = dict()
    for parallelsentence in CEJcmlReader(jcmlfilename).get_parallelsentences():
        ranking, description = ranker.rank_sentence(parallelsentence)
        ranking.sort(key=lambda x: int(x.get_attribute("system")))
        print ranking
        for rank, sentence in ranking:
            if rank=="1":
                selected_sentence = sentence
                system_name = sentence.get_attribute("system")
                counts[system_name] = counts.setdefault(system_name, 0) + 1
                outputfile.write("\n".format(selected_sentence.get_string()))
                break
                
    outputfile.close()                
    logfile = open(sys.argv[3]+".log", 'w')
    for system_name in counts.keys():
        logfile.write("{}:{}\n".format(system_name, counts[system_name]))
    logfile.close()
        
        
            