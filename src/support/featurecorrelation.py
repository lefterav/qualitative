'''
Created on Jan 23, 2013

@author: Eleftherios Avramidis
'''

import Orange

import sys
from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange
if __name__ == '__main__':
    meta_attributes = "testset,judgement_id,langsrc,langtgt,ps1_judgement_id,ps2_judgement_id,id,tgt-1_score,tgt-1_system,tgt-2_score,tgt-2_system,document_id,judge_id,segment_id"
    hidden_attributes = "tgt-1_berkeley-tree,tgt-2_berkeley-tree,src_berkeley-tree,rank_diff,tgt-1_ref-lev,tgt-1_ref-meteor_score,tgt-1_ref-meteor_fragPenalty,tgt-1_ref-meteor_recall,tgt-1_ref-meteor_precision,tgt-1_ref-bleu,tgt-2_ref-lev,tgt-2_ref-meteor_score,tgt-2_ref-meteor_fragPenalty,tgt-2_ref-meteor_recall,tgt-2_ref-meteor_precision,tgt-2_ref-bleu"

    input_filename = sys.argv[1]
    if input_filename.endswith(".jcml"):
        tab_filename = input_filename.replace(".jcml",".tab"),
        input_filename = CElementTreeJcml2Orange(input_filename, 
                                                 sys.argv[2], 
                                                 [], #all 
                                                 meta_attributes, 
                                                 
                                                 hidden_attributes=hidden_attributes)
        input_file = tab_filename
    table = Orange.data.Table()
    classname = sys.argv[2]
    
    new_domain = Orange.data.Domain([a for a in table.domain.variables if a.name != classname], table.domain[classname])
    new_data = Orange.data.Table(new_domain, table)
    
    def print_best_100(ma):
        for m in ma[:100]:
            print "%5.3f %s" % (m[1], m[0])
    

    
    print 'Relief:\n'
    meas = Orange.feature.scoring.Relief(k=20, m=50)
    mr = [ (a.name, meas(a, new_data)) for a in new_data.domain.attributes]
    mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best_100(mr)
    
    print "InfoGain\n"
    
    meas = Orange.feature.scoring.InfoGain()
    mr = [ (a.name, meas(a, new_data)) for a in new_data.domain.attributes]
    mr.sort(key=lambda x: -x[1]) #sort decreasingly by the score
    print_best_100(mr)
