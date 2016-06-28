#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
from collections import defaultdict
import gzip
import glob
import csv
import math
import random
import time
from scipy.special import erfc
import logging as log

alpha = 0.05

variants_definitions = {
 
        'wmt12' : {
            '<' : { '<': 1 , '=':-1 , '>':-1  },
            '=' : { '<':'X', '=':'X', '>':'X' },
            '>' : { '<':-1 , '=':-1 , '>': 1  },
            },

        'wmt13' : {
            '<' : { '<': 1 , '=':'X', '>':-1  },
            '=' : { '<':'X', '=':'X', '>':'X' },
            '>' : { '<':-1 , '=':'X', '>': 1  },
            },
        
        'wmt14' : {
            '<' : { '<': 1 , '=': 0 , '>':-1  },
            '=' : { '<':'X', '=':'X', '>':'X' },
            '>' : { '<':-1 , '=': 0 , '>': 1  },
            },

        'xties' : {
            '<' : { '<': 1 , '=': 0 , '>':-1  },
            '=' : { '<': 0 , '=': 1 , '>': 0  },
            '>' : { '<':-1 , '=': 0 , '>': 1  },
            },

        }


class MetricLanguagePairData(defaultdict):
    """ Stores metric scores for given metric and for given language direction.
    The keys of this dictionary like object are names of system and values are
    dictionaries mapping from segment to score """

    def __init__(self):

        # values are dictionaries mapping segment number to actual metric score
        # The underlying dictionary is indexed by system name and its
        defaultdict.__init__(self, dict)

    def kendall_tau(self, human_comparisons, count_length, variant='wmt14'):
        
        thislogger = log.getLogger(__name__)
        #thislogger.setLevel(log.DEBUG)

        try:
            coeff_table = variants_definitions[variant]
        except KeyError:
            raise ValueError("There is no definition for %s variant" % variant)

        numerator = 0
        denominator = 0
        
        numerator_length = defaultdict(float)
        denominator_length = defaultdict(float)
        comparisons_length = defaultdict(int)

        # Iterate all human comparisons
        for segment, sys1, sys2, human_comparison, ranking_length in human_comparisons:

            sys1_metric_score = self[sys1].get(segment, None)
            sys2_metric_score = self[sys2].get(segment, None)

            if(sys1_metric_score is None or sys2_metric_score is None):
                return None

            # Get the metric comparison 
            # (here the relation '<' means "is better then")
            compare = lambda x, y: '<' if x > y else '>' if x < y else '='
            metric_comparison = compare(sys1_metric_score, sys2_metric_score)

            # Adjust the numerator and denominator according the table with coefficients
            coeff = coeff_table[human_comparison][metric_comparison]
               
            if coeff != 'X':
                numerator += coeff
                denominator += 1
                numerator_length[ranking_length] += coeff
                denominator_length[ranking_length] += 1
            comparisons_length[ranking_length] += 1
            
        tau = 1.00 * numerator / denominator
        
        sum_inv_variance = 0
        sum_inv_variance_tau = 0
        for n, numerator_n in numerator_length.iteritems():
            denominator_n = denominator_length[n]
            tau_n = 1.00 * numerator_n / denominator_n
            counts_n = count_length[n]
            #print "Counts {} solved as :".format(n), counts_n
            #inverted variance:
            inv_variance_n = counts_n * 9.00 * n * (n - 1) / (4.00 * n + 10)
            thislogger.debug("inv_variance_n = {counts_n} * 9 * {n} * ({n} - 1) / (4.00 * {n} + 10) ".format(n=n, counts_n=counts_n))
            thislogger.debug("inv_variance_n = {}".format(inv_variance_n))
            sum_inv_variance += inv_variance_n
            thislogger.debug("sum_inv_variance += {}".format(inv_variance_n))
            sum_inv_variance_tau += inv_variance_n * tau_n
        weighed_variance = 1.00 / sum_inv_variance
        weighed_tau = sum_inv_variance_tau / sum_inv_variance
        # z would follow the standard distribution
        z = (weighed_tau / math.sqrt(weighed_variance))
        pvalue = erfc(abs(z) / math.sqrt(2)) 
        # Return the Kendall's tau
        return tau, weighed_tau, pvalue


class SegmentLevelData(object):
    """ Stores scores for all metrics, language directions and systems. Also stores human scores
    for all language direction and systems.
    """

    def __init__(self):
        self.metrics_data = defaultdict(MetricLanguagePairData) # indexed by tuples (metric, direction)
        self.human_comparisons = defaultdict(list) # indexed by language direction:

    def add_metrics_data(self, file_like):
        for file in glob.glob(file_like):
            with gzip.open(file, mode="rt") as f:
                for metric, lang_pair, test_set, system, segment, score in csv.reader(f, delimiter='\t'):
                    # Convert numerical values
                    segment = int(segment)
                    score = float(score)

                    if segment not in self.metrics_data[metric, lang_pair][system]:
                        self.metrics_data[metric, lang_pair][system][segment] = score
                    else:
#                        print("Warning: ", metric, lang_pair, system, segment, "Segment score already exists." ,file=sys.stderr)
                        pass

    def add_human_data(self, file_like):
        for file in glob.glob(file_like):
            with gzip.open(file, mode="rt") as f:
                for line in csv.DictReader(f):
                    direction = "dummy"

                    #direction = line['system1Id'].rsplit('.', 2)[1]
                    segment = int(line['segmentId'])

                    extract_system = lambda x: '.'.join(x.split('.')[1:-2])

                    id1 = extract_system(line['system1Id'])
                    rank1 = int(line['system1rank'])
                    id2 = extract_system(line['system2Id'])
                    rank2 = int(line['system2rank'])

                    # Extract all comparisons (Making sure that two systems are extracted only once)
                    # Also the extracted relation '<' means "is better than"
                    compare = lambda x, y: '<' if x < y else '>' if x > y else '='
                    extracted_comparisons = [
                            (segment, id1, id2, compare(rank1, rank2))
                        ]

                    self.human_comparisons[direction] += extracted_comparisons

    def extracted_pairs(self, direction):
        return len(self.human_comparisons[direction])

    def compute_tau_confidence(self, metric, direction, variant, count_length, samples=1000):
        if (metric,direction) not in self.metrics_data:
            return None, None, None, None

        metric_data = self.metrics_data[metric,direction]
        comparisons = self.human_comparisons[direction]

        tau, weighed_tau, pvalue = metric_data.kendall_tau(comparisons, count_length, variant)
        confidence = self.compute_confidence(metric_data, comparisons, variant, count_length, samples)

        return tau, confidence, weighed_tau, pvalue

    def compute_confidence(self, metric_data, comparisons, variant, count_length, samples=1000):
        if samples == 0:
            return None

        # Setting random seed here, to generate same samples for all metrics and directions
        random.seed(int(time.time()))

        taus = []
        for _ in range(samples):
            sample = (random.choice(comparisons) for _ in comparisons) 
            tau, _, _ = metric_data.kendall_tau(sample, count_length, variant)
            if tau is None:
                return None
            taus.append(tau)

        taus.sort()
        
        #avg_tau = sum(taus) / len(taus)
        
        l_tau = taus[int(samples * alpha/2)]
        r_tau = taus[int(samples * (1 - alpha/2))]
        return abs(l_tau - r_tau) / 2

    def metrics(self):
        return list(set(pair[0] for pair in self.metrics_data.keys()))


def safe_avg(iterable):
    filtered = list(filter(None, iterable))
    try:
        return 1.00* sum(filtered) / len(filtered)
    except ZeroDivisionError:
        return None

def safe_max(iterable):
    maximum = None
    for item in filter(None, iterable):
        if maximum is None:
            maximum = item
        else:
            maximum = max(maximum, item)
    return maximum

