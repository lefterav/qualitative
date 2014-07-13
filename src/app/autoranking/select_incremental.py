'''
Created on 7 Jul 2014

@author: Eleftherios Avramidis
'''

from ml.lib.orange import OrangeRuntimeRanker 
from io_utils.ce.cejcml import CEJcmlReader 
from collections import OrderedDict
import sys

if __name__ == '__main__':
    classifiername = sys.argv[1]
    ranker = OrangeRuntimeRanker(classifiername)

    jcmlfilename = sys.argv[2]
    outputfile = open(sys.argv[3], 'w')
    counts = dict()
    text = dict()
    for parallelsentence in CEJcmlReader(jcmlfilename, all_target=True).get_parallelsentences(False):
#        text = dict([(t.get_attribute("system"), t.get_string()) for t in parallelsentence.get_translations()])
#        print text
        ranking, description = ranker.rank_sentence(parallelsentence)
        #ranking.sort(key=lambda x: x[1].get_attribute("system"))

        for rank, sentence in ranking:
            if rank=="1":
                selected_sentence = sentence
                system_name = sentence.get_attribute("system")
                #selected_text = text[system_name]
                selected_text = selected_sentence.get_string().replace("\r", "").replace("\n", "")
                counts[system_name] = counts.setdefault(system_name, 0) + 1
                outputfile.write("{}\n".format(selected_text))
                break
                
    outputfile.close()                
    logfile = open(sys.argv[3]+".log", 'w')
    for system_name in counts.keys():
        logfile.write("{}:{}\n".format(system_name, counts[system_name]))
    logfile.close()
        
        
            
