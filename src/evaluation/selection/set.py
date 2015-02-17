'''
Created on 16 Feb 2015

@author: Eleftherios Avramidis
'''
from collections import defaultdict, OrderedDict
from operator import attrgetter

def evaluate_selections(parallelsentences, 
                        metrics=[], 
                        function=max,
                        rank_name="rank-predicted"):
    selected_sentences = []
    scores = OrderedDict()
    selected_systems = defaultdict(int) #collect the winnings of each system
    
    
    best_rank = 
            
