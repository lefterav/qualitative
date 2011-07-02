'''

@author: lefterav
'''
import sys
from sentence.rankhandler import RankHandler
from xml.sax import make_parser


if __name__ == '__main__':
#    from autoranking import AutoRankingExperiment
#    exp = AutoRankingExperiment()
#    scoresprint = exp.print_system_score(sys.argv[1], sys.argv[2])
#    f = open(sys.argv[3], 'w')
#    for entry in scoresprint:
#        f.write(entry)
#    f.close()
    from io.saxscoring import SaxSystemScoring
    saxreader = SaxSystemScoring("rank", sys.argv[2], sys.argv[3])
    fileinput = open(sys.argv[1])
    
    myparser = make_parser()
    myparser.setContentHandler(saxreader)
    myparser.parse(fileinput)
    fileinput.close

        