'''
Experiments with different Lucy versions

Created on 21 Apr 2016

@author: Eleftherios Avramidis
'''
import sys
import argparse
from support.preprocessing.csv2moses import get_source_sentences,\
    select_translator, translate_sentences
import csv
from mt.lucy import LucyWorker, AdvancedLucyWorker
from pip._vendor.requests.packages.urllib3.packages.six import advance_iterator
from featuregenerator.reference.bleu import BleuGenerator
from featuregenerator.reference.meteor.meteor import MeteorGenerator
from _collections import defaultdict

MOSES_URI = "http://localhost:9200"
LUCY_URI = "http://msv-3251.sb.dfki.de:8080/AutoTranslateRS/V1.2/mtrans/exec"


def create_worker(**kwargs):
    worker = AdvancedLucyWorker(**kwargs)
    filename = "unknowns_{unknowns}.menu_items_{menu_items}.menu_quotes_{menu_quotes}.menu_translator_{menu_translator}.normalize_{normalize}.wc_{suppress_where_it_says}.txt".format(**kwargs)
    return worker, filename

if __name__ == '__main__':
    input = sys.stdin 
    output = sys.stdout
    
    
    source_language = "en"
    target_language = "de"
    
    #param_normalize = [False, True]
    param_normalize = [True]
    #param_unknowns = [False, True]
    param_unknowns = [True]
    #param_menu_items = [False, True]
    param_menu_items = [True]
    param_menu_quotes = [False]
    #param_menu_translator = ["Lucy", "Moses"]
    param_menu_translator = ["Moses"]
    param_suppress_where_it_says = [True]
    
    workers = []
    
    for normalize in param_normalize:
        for unknowns in param_unknowns:
            for suppress_where_it_says in  param_suppress_where_it_says:
                for menu_items in param_menu_items:
                    if menu_items:
                        for menu_quotes in param_menu_quotes:
                            for menu_translator in param_menu_translator:
                                translator, filename = create_worker( 
                                    url=LUCY_URI, moses_uri=MOSES_URI, 
                                    unknowns=unknowns, 
                                    menu_items=menu_items, 
                                    menu_quotes=menu_quotes, 
                                    menu_translator=menu_translator, 
                                    normalize=normalize,
                                    source_language=source_language, 
                                    target_language=target_language,
                                    suppress_where_it_says=suppress_where_it_says)
                                workers.append((translator, filename))
                                
                    else:
                        menu_quotes = False
                        menu_translator = None
                        translator, filename = create_worker( 
                            url=LUCY_URI, moses_uri=MOSES_URI, 
                            unknowns=unknowns, 
                            menu_items=menu_items, 
                            menu_quotes=menu_quotes, 
                            menu_translator=menu_translator, 
                            normalize=normalize,
                            source_language=source_language, 
                            target_language=target_language,
                            suppress_where_it_says=suppress_where_it_says)
                        workers.append((translator, filename))

    description_params = ["menus", "menu_items", "unk_count", "unk_replaced"]

    d = defaultdict(int)
    
    for worker, filename in workers:
        print filename
        infile = open(sys.argv[1])
        outfile = open(sys.argv[2] + "_" + filename, 'w')
        outfile_stats = open(sys.argv[2] + "_" + filename + ".stats", 'w')
        for line in infile:
            translation, translation_description = worker.translate(line)
            print >> outfile, translation
            for param in description_params:
                d[param] += translation_description.setdefault(param, 0)
        
        print >> outfile_stats, "\t".join([k for k, _ in d.iteritems()])
        print >> outfile_stats, "\t".join([str(v) for _, v in d.iteritems()])
        outfile_stats.close()
        outfile.close()
        infile.close()
