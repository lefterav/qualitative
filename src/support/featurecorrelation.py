'''
Created on Jan 23, 2013

@author: Eleftherios Avramidis
'''

import Orange
import orange

import sys
import os

from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml
from io_utils.input.xmlreader import XmlReader
from sentence.pairwisedataset import PairwiseDataset
from sentence.pairwisedataset import AnalyticPairwiseDataset

pairwise=True

#function copied from rank widget
def getDiscretizedData(data, intervals):
            discretizer = orange.EquiNDiscretization(numberOfIntervals=intervals)
            contAttrs = filter(lambda attr: attr.varType == orange.VarTypes.Continuous, data.domain.attributes)
            at = []
            attrDict = {}
            for attri in contAttrs:
                try:
                    nattr = discretizer(attri, data)
                    at.append(nattr)
                    attrDict[attri] = nattr
                except:
                    pass
            discretizedData = data.select(orange.Domain(at, data.domain.classVar))
            discretizedData.setattr("attrDict", attrDict)
            return discretizedData



if __name__ == '__main__':

    try:
        pairwise = not (sys.argv[3]=='--nopairs')
    except:
        pairwise = True

    #if pairwise:
    meta_attributes = "testset,judgement_id,langsrc,langtgt,ps1_judgement_id,ps2_judgement_id,id,tgt-1_system,tgt-2_system,document_id,judge_id,segment_id,translator_id,doc_id".split(',')
    hidden_attributes = "tgt-1_berkeley-tree,tgt-2_berkeley-tree,src_berkeley-tree,rank_diff,tgt-1_ref-lev,tgt-1_ref-meteor_score,tgt-1_ref-meteor_fragPenalty,tgt-1_ref-meteor_recall,tgt-1_ref-meteor_precision,tgt-1_ref-bleu,tgt-2_ref-lev,tgt-2_ref-meteor_score,tgt-2_ref-meteor_fragPenalty,tgt-2_ref-meteor_recall,tgt-2_ref-meteor_precision,tgt-2_ref-bleu,tgt-1_rank,tgt-2_rank".split(',')
    hidden_attributes.extend(meta_attributes)
    #else:
    #    meta_attributes = ""


    tempdir = "/tmp"

    input_filename = sys.argv[1]

    if pairwise:
        class_type = "d"
    else:
        class_type = "c"
 
    if input_filename.endswith(".jcml"):
        pairwise_filename = os.path.join(tempdir, os.path.basename(input_filename.replace(".jcml",".pair.jcml")))
        
        tab_filename = os.path.join(tempdir, os.path.basename(input_filename.replace(".jcml",".tab")))
        
        if pairwise:
            sys.stderr.write('pairwising XML file {} to {} ...\n'.format(input_filename,pairwise_filename))
            Parallelsentence2Jcml(AnalyticPairwiseDataset(XmlReader(input_filename)).get_parallelsentences()).write_to_file(pairwise_filename)
        else:
            pairwise_filename = input_filename
        sys.stderr.write('converting XML file {} to tab ...\n'.format(pairwise_filename))
        CElementTreeJcml2Orange(pairwise_filename, 
                                                 sys.argv[2], 
                                                 [], #all 
                                                 meta_attributes, 
                                                 tab_filename,
                                                 hidden_attributes=hidden_attributes,
                                                 nullimputation=True,
                                                 class_type=class_type).convert()
        input_filename = tab_filename
        sys.stderr.write('created converted file {} ...'.format(input_filename))
    table = Orange.data.Table(input_filename)
    classname = sys.argv[2]
    
    #new_domain = Orange.data.Domain([a for a in table.domain.variables if a.name != classname], table.domain[classname])
    #new_data = Orange.data.Table(new_domain, table)
    data = table
    import math
    def print_best(ma):
        #remove nan because it is confusing the sorted
        ma = [item for item in ma if not math.isnan(float(item[1]))]
        ma = sorted(ma, key=lambda item: abs(item[1]), reverse=True)
        for m in ma[:1000]: #display all practically :-)
            print "%5.3f %s" % (m[1], m[0])
    

    
    print 'Relief:\n'
    meas = Orange.feature.scoring.Relief(k=20, m=50)
    mr = [ (a.name, meas(a, data)) for a in data.domain.attributes]
    #mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best(mr)
    
     
    print "InfoGain\n"
    data = getDiscretizedData(data,100)
 
    meas = Orange.feature.scoring.InfoGain()
    mr = [ (a.name, meas(a, data)) for a in data.domain.attributes]
    #mr.sort(key=lambda x: -x[1]) #sort decreasingly by the scorei
    print_best(mr)
    
