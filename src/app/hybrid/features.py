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

    #CEJcmlReader(filename).get_attribute_statistics(fileobject=f)
    f.close()
    
    #===========================================================================
    # Part 2: write advanced scoring in file 
    #===========================================================================
    measures = [Relief(), MDL(),]
    
    
    attset = {}
    
    f = open(os.path.join(location, "stats_scoring.csv"), 'w')
    f.write("\t{}".format("\t".join([m.__class__.__name__ for m in measures])))
    for metric in metrics:
        f.write("{}\n".format(metric))
        data = dataset_to_instances(filename=filename, class_name=metric, tempdir="./tmp")
        attset[metric] = defaultdict(list)
        print type(attset)
        n = 50
        for attr in data.domain.attributes:
            if attr.name in ["id", "judgement_id"]:
                continue
            line = []
            for meas in measures:
                try:
                    result = meas(attr, data)
                except:
                    result = 0
                line.append(str(result))
                attset[metric][meas.__class__.__name__].append((attr.name, result)) 
            f.write("{}\t{}\n".format(attr.name, "\t".join(line)))
        print type(attset)
        #order attributes based on score 
    f.close()
    print type(attset)
    
    #====
    #  Part 3: export ordered lines of attributes for use in configuration file
    #=====
    
    
    for metric in metrics:
        print type(attset)
        for measure in attset[metric]:
            #try:
            print attset
            print attset[metric]
            print type(attset[metric])
            attlist = attset[metric][measure]
            attlist = sorted(attlist, key=itemgetter(1), reverse=True)
            if not attlist:
                continue
            pairwise_names = [name for name,_ in attlist]
            #except AttributeError:
            #    continue
            wrapped_attribute_set = AttributeSet()
            wrapped_attribute_set.set_names_from_pairwise(pairwise_names)
            print '{}\t{}\t{} = "{}"'.format(metric, measure, "attset_generic", ",".join(wrapped_attribute_set.parallel_attribute_names))
            print '{}\t{}\t{} = "{}"'.format(metric, measure, "attset_source", ",".join(wrapped_attribute_set.source_attribute_names))        
            print '{}\t{}\t{} = "{}"'.format(metric, measure, "attset_target", ",".join(wrapped_attribute_set.target_attribute_names))
        
        
    
    
    #===========================================================================
    # Part 3: write attribute names as chosen above in the respective order for further use
    #===========================================================================
