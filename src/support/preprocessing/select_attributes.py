'''
Created on 6 Mar 2012

@author: elav01
'''

from io_utils.input.jcmlreader import JcmlReader
import sys


if __name__ == '__main__':
    dataset = JcmlReader(sys.argv[1]).get_dataset()                    
    expressions = sys.argv[2:]
    print expressions
#                   ["bb_.*"], #baseline
#                   #20first with gain radio with manual removal
#                   ["tgt-1_berkeley-n","src_grammar_subject_verb_agreement_matches","src_grammar_noun_adjective_confusion_chars","src_grammar_wrong_word_matches","tgt-1_lgt_pp_v_plural_5_","tgt-1_lgt_nom_adj_fem_6_","tgt-1_lgt_double_punctuation","tgt-1_lgt_comma_parenthesis_whitespace","src_grammar_wrong_word","tgt-1_lgt_pp_v_singular_4_","src_style_do_not_use_complex_coordinations_chars","src_style_avoid_multiple_negation_chars","src_grammar_wrong_verb_form", "src_grammar_np_number_agreement_chars", "tgt-1_lgt_det_nom_masc_3", "src_style_repeat_modal_verb", "src_grammar_np_number_agreement", "src_style_disambiguate_that", "src_style_verb_close_to_subject_chars"],
#                   #20first with infgain and manual removal of obvious correlations
#                   ["tgt-1_berkeley-best-parse-confidence","tgt-1_berkley-loglikelihood","src_berkley-loglikelihood","src_berkeley-avg-confidence","src_parse-NP","tgt-1_berkeley-avg-confidence","tgt-1_parse-NP","src_parse-NN","tgt-1_parse-PP","tgt-1_berkeley-n_ratio","src_parse-VB","judgement_id","src_berkeley-n","tgt-1_parse-S","tgt-1_parse-NP_ratio","tgt-1_berkeley-n","tgt-1_parse-VB_ratio","tgt-1_parse-NN_ratio","tgt-1_d_a5_avg","tgt-1_parse-PP_ratio"],
#                   #source_target_language_tools
#                   #["src_grammar.*", "src_style.*", "tgt-1_lgt_.*"]
#                   ["tgt-1_berkeley-n", "tgt-1_berkeley.*ratio"]           
#                   ]
    attributes = dataset.select_attribute_names(expressions)
    if attributes:
        print ",".join(attributes)
#        print '["%s"]' % '","'.join(attributes)
        
    
