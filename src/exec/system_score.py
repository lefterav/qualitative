'''

@author: lefterav
'''
import sys


if __name__ == '__main__':
    from autoranking import AutoRankingExperiment
    exp = AutoRankingExperiment()
    exp.print_system_score(sys.argv[0], sys.argv[1])