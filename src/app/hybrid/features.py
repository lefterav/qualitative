'''
Created on 18 Feb 2015

@author: Eleftherios Avramidis
'''
from dataprocessor.ce.cejcml import CEJcmlReader
import sys, os
from dataprocessor.ce.cejcml2orange import CElementTreeJcml2Orange
from ml.lib.orange.ranking import dataset_to_instances
from Orange.feature.scoring import Relief, InfoGain, GainRatio, Gini, Relevance, MDL, Distance 
from sentence.parallelsentence import AttributeSet
from collections import defaultdict
from operator import itemgetter


if __name__ == '__main__':
    filename = sys.argv[1]
    metrics = sys.argv[3:]
    location = sys.argv[2]
    

    #===========================================================================
    # Part 1: write basic statistics in file 
    #===========================================================================
    
    f = open(os.path.join(location, "stats_basic.csv"), 'w')

    CEJcmlReader(filename).get_attribute_statistics(fileobject=f)
    f.close()
    
    #===========================================================================
    # Part 2: write advanced scoring in file 
    #===========================================================================
    measures = [Relief(), InfoGain(), GainRatio(), Gini(), Relevance(), MDL(), Distance()]
    
    
    attset = {}
    
    f = open(os.path.join(location, "stats_scoring.csv"), 'w')
    f.write("\t{}".format("\t".join([m.__class__.__name__ for m in measures])))
    for metric in metrics:
        f.write("{}\n".format(metric))
        data = dataset_to_instances(filename=filename, class_name=metric)
        attset[metric] = defaultdict(list)
        
        n = 50
        for attr in data.domain.attributes:
            if attr.name in ["id", "judgement_id"]:
                continue
            line = []
            for meas in measures:
                try:
                    result = str(meas(attr, data))
                except:
                    result = ""
                line.append(result)
                attset[metric][meas].append((attr.name, result)) 
            f.write("{}\t{}\n".format(attr.name, "\t".join(line)))
        
        #order attributes based on score 
        attset[metric][meas] = sorted(attset[metric][meas], key=itemgetter(1), reverse=True)
    f.close()
    
    
    #====
    #  Part 3: export ordered lines of attributes for use in configuration file
    #=====
    
    
    for metric in metrics:
        for measure in measures:
            try:
                pairwise_names = [name for name,_ in attset[metric][measure]]
            except AttributeError:
                continue
            attset = AttributeSet()
            attset.set_names_from_pairwise(pairwise_names)
            print '{}\t{}\t{} = "{}"'.format(metric, measure.__class__.__name__, "attset_generic", ",".join(attset.parallel_attribute_names))
            print '{}\t{}\t{} = "{}"'.format(metric, measure.__class__.__name__, "attset_source", ",".join(attset.source_attribute_names))        
            print '{}\t{}\t{} = "{}"'.format(metric, measure.__class__.__name__, "attset_target", ",".join(attset.target_attribute_names))
        
        
    
    
    #===========================================================================
    # Part 3: write attribute names as chosen above in the respective order for further use
    #===========================================================================