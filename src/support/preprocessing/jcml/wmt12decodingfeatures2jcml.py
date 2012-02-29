'''
Created on 29 Feb 2012

@author: elav01
'''
import re
import sys
import os
import subprocess
import numpy
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

from io.sax.saxps2jcml import Parallelsentence2Jcml
from io.input.jcmlreader import JcmlReader


def process(path):
    files = [(int(re.findall("(.*)\.sgml", f)[0]), f) for f in os.listdir(path) if f.endswith("sgml")]
    atts_vector = []
    for sentence_id, filename in sorted(files):
        filename = os.path.join(path, filename)
        print filename
        file = open(filename, 'r')
        
        file_content = file.read()
        file.close()
        
        #SCORES
        pattern = "SCORES \(UNWEIGHTED/WEIGHTED\): d: ([\d\-\.]*) w: ([\d\-\.]*) u: ([\d\-\.]*) d: ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) lm: ([\d\-\.]*) tm: ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*) ([\d\-\.]*)"
        values = re.findall(pattern, file_content)[0]
        [score_d, score_w, score_u, score_d1, score_d2, score_d3, score_d4, score_d5, score_d6, score_lm, score_tm1, score_tm2, score_tm3, score_tm4, score_tm5] = values
        
        sentence_atts = dict(score_d = score_d, score_w=score_w, 
                    score_d1=score_d1, score_d2=score_d2, score_d3=score_d3, score_d4=score_d4, score_d5=score_d5, score_d6=score_d6,
                    score_lm=score_lm, score_tm1=score_tm1, score_tm2=score_tm2, score_tm3=score_tm3, score_tm4=score_tm4, score_tm5=score_tm5 )
        
        #GRAPH
        graph_content = file_content.split("<wgraph>")[1]
        pattern = "([\w]*)=([\d\-\.\,\ ]*)\s*"
        
        atts = {}
        graph_rows = re.findall(pattern, graph_content)
        for (graph_feature_name, graph_feature_value)in graph_rows:
            
            if graph_feature_name == "a":
                atts.update(_split_a_vector(graph_feature_value))
            elif graph_feature_name == "r":
                atts.update(_split_r_vector(graph_feature_value))
                
            elif graph_feature_name in ["UTTERANCE", "VERSION", "w"]:
                pass
            else:
                if graph_feature_name == "pC":
                    graph_feature_value = graph_feature_value.strip()[:-1]
            
                try:
                    atts[graph_feature_name].append(float(graph_feature_value))
                except KeyError:
                    atts[graph_feature_name] = [float(graph_feature_value)]
                
        #now calculate avg
        
        for graph_feature_name, graph_feature_values in atts.iteritems():
            sentence_atts["{0}_avg".format(graph_feature_name)] = numpy.average(graph_feature_values)
            sentence_atts["{0}_std".format(graph_feature_name)] = numpy.std(graph_feature_values)
            sentence_atts["{0}_var".format(graph_feature_name)] = numpy.var(graph_feature_values)
        
        atts_vector.append(sentence_atts)
        
    return atts_vector


def _split_a_vector(graph_feature_value):
    return {}

def _split_r_vector(graph_feature_value):
    return {}
                        

if __name__ == '__main__':
    input_path = sys.argv[1] #"/home/elav01/taraxu_data/wmt12/quality-estimation/training_set/decoding"
    input_jcml = sys.argv[2] #"/home/elav01/taraxu_data/wmt12/quality-estimation/training_set/training.jcml"
    output_jcml = sys.argv[3] #"/home/elav01/taraxu_data/wmt12/quality-estimation/training_set/training.decoding.es.f.jcml"
    
    att_vector = process(input_path)
    
    dataset = JcmlReader(input_jcml).get_dataset()
    dataset.add_attribute_vector(att_vector)
    Parallelsentence2Jcml(dataset.get_parallelsentences()).write_to_file(output_jcml)