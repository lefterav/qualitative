'''
Created on 07 Mar 2012

@author: Eleftherios Avramidis
'''

from suite import AutorankingSuite
import argparse 
import sys
import os
import logging
from decimal import Decimal
from numpy import mean, std
from collections import OrderedDict
from fnmatch import fnmatch
from operator import itemgetter
from math import pow
 
"""
Gathers the results from the app folders created with python Experiment Suite
"""





def retrieve_results(mysuite, path, reps = [0], tags='all'):
    """
    Parallelizes and aligned the vectors provided by the Experiment Suite API
    @param mysuite: instance of the Experiment Suite or subclass
    @type mysuite: L{ExperimentSuite}
    @param path: the directory that will be searched for results. It needs to have the structure suported by Experiment Suite
    @type path: str 
    @param reps: a list or a range of repetition values that need to be checked. For simple experiments only one repetition exists, so the default value is 0
    @type reps: [int, ...]
    @return: A list of with one tuple per app. Each tuple contains a dictionary of the app parameters and a a dictionary of the result values
    @rtype: [({parameter_name:parameter_value},{result_name:result_value}), ...] 
    The key of each entry is a tuple containing (attribute_set,classifier_name,discretization,filterscorediff) and 
    its value is a list of (float) values, respectively to their names entered in the list 'required_feature_names'
    """
    results = []
    exps = mysuite.get_exps(path=path)
    logging.info("Found %s experiments", len(exps))    
    logging.debug("exps: %s", exps)
    result_names = set()
    
    #browse app directories one by one
    for exp in exps:
        try:
            logging.debug("Getting histories over repetitions for mean")
            values = mysuite.get_histories_over_repetitions(exp=exp, tags=tags, aggregate=mean)
            logging.debug("Getting histories over repetitions for std")
            values_std = mysuite.get_histories_over_repetitions(exp=exp, tags=tags, aggregate=std)
        except ValueError:
            continue
        values_std = OrderedDict([("{}_std".format(k),v) for k,v in values_std.iteritems()])
        
        #values_rep = mysuite.get_histories_over_repetitions(exp=exp, tags='all', aggregate=list)
        #for rep, key, vs in enumerate(values_rep.iteritems()):
        #    for v in vs:
        #        values["rep-{}_{}".format(rep, key)] = v
                
        values.update(values_std)
        #if values:
        #    params = mysuite.get_params(exp)
        #    params["app"] = os.path.basename(os.path.dirname(exp))
        #    results.append((params, values))
        
        #         for rep in reps:
        #             #get a dictionary with all result values for the current app
        #             values = mysuite.get_value(exp, rep, 'all')
        #             if values:
        #                 params = mysuite.get_params(exp)
        #                 params["app"] = os.path.basename(os.path.dirname(exp))
        #                 results.append((params, values))


        if values:
            params = mysuite.get_params(exp)
            params["app"] = os.path.basename(os.path.dirname(exp))
            results.append((params, values))

        logging.info("found %s experiments", len(results))
        
    return results

                
       
def get_tabfile(results, preferred_params=[], preferred_scores=[], display_header=True, delimiter="\t", decimals=3, limit=None, sort_column=1, sort_reverse=False):

    quantize = Decimal(str(pow(10, -1*decimals)))
    logging.warn("Decimals {}, quantize {}".format(decimals, quantize))
    #get a list with the result names
    param_keys = set()
    score_keys = set()
    for params, values in results:
        param_keys.update(params.keys())
        score_keys.update(values.keys())
    
#    keys_toremove = set([param_key for param_key in param_keys if param_key.startswith("attset_")])
#    keys_toremove.add('iterations')
#    keys_toremove.add('repetitions')
#    keys_toremove.add('path')
#    keys_toremove.add('test_set')
#    keys_toremove.add('hidden_attributes')
#    
    
#    param_keys = param_keys - keys_toremove     
    
    if not preferred_params:
        preferred_params = param_keys

    if not preferred_scores:
        preferred_scores = list(score_keys)
    else:    

        new_preferred_scores = []
        for preferred_score in preferred_scores:
            for score_key in score_keys:
               if fnmatch(score_key, preferred_score):
                   new_preferred_scores.append(score_key)
    
        preferred_scores = new_preferred_scores

    if display_header:
        print delimiter.join(preferred_params) + delimiter + delimiter.join(preferred_scores)
    
    results = sorted(results, key=itemgetter(0))

    tab_rows = [] #will contain both params and values in one row

    for params, values in results:

        #retain only the preferred params
        params = [str(params.setdefault(param_name,"None")) for param_name in preferred_params]
        
        onlyvalues = []
        
        #collect a list with the values
        for key in preferred_scores:

            #extract from array, if possible
            try:
                val = float(values[key][0])
            except IndexError:
                try:
                    val = values[key]
                except KeyError:
                    val = ''

            try:
                val = Decimal(val).quantize(quantize)
            except Exception as e:
                pass
                logging.warn("'{}' while  quantizing {}{}".format(e, key, val))
            onlyvalues.append(str(val))
                    
        #print delimiter.join(params) + delimiter + delimiter.join(onlyvalues)
        tab_rows.append(params + onlyvalues)

    tab_rows.sort(key=itemgetter(sort_column), reverse=sort_reverse)
    row_counter = 0
    
    for row in tab_rows:        
        # nan values should be ignored when sorting
        if limit is not None and row[sort_column].endswith('NaN'):
            continue
        row_counter+=1
        if limit is not None and row_counter > limit:
            break
        print delimiter.join(row)
            
if __name__ == "__main__":
    
    #dev example 
    #python2.7 check.py --path /home/Eleftherios Avramidis/taraxu_data/selection-mechanism/emnlp/app/4b --reps 0 --config config/autoranking.suite.bernux.cfg --params app classifier att mode ties include_references  > test.csv
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--path', nargs=1,
                   help='the path were experiments will be found')
    parser.add_argument('--reps', type = int, nargs='*',                   
                   help='list of repetition ids to keep (default: 0)')
    
    parser.add_argument('--params', nargs='*',                   
                   help='Names of parameters to be displayed (default: all)')
    
    parser.add_argument('--metrics', nargs='*', default='all',                   
                   help='Names of metrics to be displayed (default: all)')
    
    parser.add_argument('--config', nargs=1,                   
                   help='the configuration file to be checked')
                   
    parser.add_argument('--logging', nargs="?", default=None,
                   help='should logging be performed, if set to True writes the debug level to debug.log, ')

    parser.add_argument('--limit', default=None, type=int, help="Limit the result to the n best after sorting")
    parser.add_argument('--sort_column', type=int, default=1, help="Index of the column to sort against")
    parser.add_argument('--sort_reverse', type=bool, default=False, help="Set True in order to sort descending")
    parser.add_argument('--decimals', type=int, default=3, help="Number of decimal digits beyond decimal point")
    parser.add_argument('--display_header', type=bool, default=True, help="Whether to display the column header")
    
    args = parser.parse_args()
    
    if args.logging:
        logging.basicConfig(filename='debug.log',level=getattr(logging, args.logging.upper()))
    
    sys.argv = [sys.argv[0]]
    sys.argv.extend(["--config", args.config])
    mysuite = AutorankingSuite()
    
    path = args.path[0]
    reps = args.reps
    preferred_params = args.params
    preferred_scores = args.metrics

    results = retrieve_results(mysuite, path, reps, preferred_scores)
    get_tabfile(results, preferred_params, preferred_scores, limit=args.limit, 
            sort_column=args.sort_column, sort_reverse=args.sort_reverse,
            display_header=args.display_header, decimals=args.decimals)
