'''
Created on Aug 4, 2011

@author: Eleftherios Avramidis
'''
from sys import argv
from io_utils.input.xmlreader import XmlReader
from io_utils.input.rankreader import RankReader
from sentence.scoring import Scoring

"""
    Reads two versions of the same dataset, one with estimated ranking and one with gold rankings. 
    It then calculates the ranking correlation coefficients. 
"""


if __name__ == '__main__':
    
    dataset1 = RankReader("/home/Eleftherios Avramidis/taraxu_data/r1/results/8-3-NEWS-de-en-ranking.xml").get_dataset()
    dataset2 = XmlReader("/home/Eleftherios Avramidis/taraxu_data/r1/machine-ranking/DE-EN_news_SRC_Trados_Lucy_Google_Moses.out.xml").get_dataset()
    
    dataset1.merge_dataset(dataset2, {"rank": "estimated_rank"}, ["id"])
    #print (Scoring(dataset1.get_parallelsentences())).get_kendall_tau_avg("rank", "estimated_rank")
    #for item in (Scoring(dataset1.get_parallelsentences())).get_kendall_tau_vector("rank", "estimated_rank"):
    #    print item
    
    #frequencies = (Scoring(dataset1.get_parallelsentences())).get_kendall_tau_freq("rank", "estimated_rank")
    #for distroclass in frequencies:
    #    print distroclass, frequencies[distroclass]
    print (Scoring(dataset1.get_parallelsentences())).selectbest_accuracy("rank", "estimated_rank")
    