
from itertools import permutations
from segment import kendall_tau
from sentence.ranking import Ranking
from math import factorial

def prob(tau, n):
    perfect_rank = range(1,n+1)
    all_ranks = list(permutations(perfect_rank))
    print all_ranks

    taus = [kendall_tau(Ranking(rank_strings), Ranking(perfect_rank)).tau for rank_strings in all_ranks]
    print taus
    print taus
    taus_count = len([t for t in taus if t >= tau])
    print taus_count
    prob = taus_count*1.00 / factorial(n)
    return prob

print prob(0.6666666, 4)
