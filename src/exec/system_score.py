'''

@author: lefterav
'''
import sys


if __name__ == '__main__':
    from autoranking import AutoRankingExperiment
    exp = AutoRankingExperiment()
    scoresprint = exp.print_system_score(sys.argv[1], sys.argv[2])
    f = open(sys.argv[3], 'w')
    for entry in scoresprint:
        f.write(entry)
    f.close()
        