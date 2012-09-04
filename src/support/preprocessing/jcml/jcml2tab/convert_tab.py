import sys
from io_utils.sax.cejcml2orange import CElementTreeJcml2Orange 


input_file = sys.argv[1]
output_file = sys.argv[2]

hidden_attributes = ["langsrc","langtgt","tgt-1_score","judgement_id","id","src","tgt-1","src_berkeley-tree","tgt-1_berkeley-tree","tgt-1_system","testset"]
active_attributes = []
meta_attributes = []
discrete_attributes = []
dir = '.'

CElementTreeJcml2Orange(input_file, 
                 "",
                 active_attributes, 
                 meta_attributes, 
                 output_file, 
                 compact_mode = True, 
                 discrete_attributes=discrete_attributes,
                 hidden_attributes=hidden_attributes,
                 get_nested_attributes=True,
                 dir=dir
                 #filter_attributes={"rank" : "0"},
#                 class_type=class_type
                )
