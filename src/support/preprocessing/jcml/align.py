'''
Created on Jun 7, 2013

@author: dupo
'''
import sys
from dataprocessor.input.jcmlreader import JcmlReader
from dataprocessor.sax.saxps2jcml import Parallelsentence2Jcml


if __name__ == '__main__':
    target_attribute_names = [sys.argv[1]]
    base_xml_filename = sys.argv[2]
    incoming_xml_filename = sys.argv[3]
    output_filename = sys.argv[4]
    try:   
        blind = (sys.argv[5] == "--blind")
    except:
        blind = False
    
    base_dataset = JcmlReader(base_xml_filename).get_dataset()
    incoming_dataset = JcmlReader(incoming_xml_filename).get_dataset()
    
    if not blind:
        keep_attributes_general = ["judgement_id","langsrc","testset","id","langtgt"]
        keep_attributes_target = ['system','rank']
    else:
        keep_attributes_general = ["langsrc","id","langtgt"]
        keep_attributes_target = []
    
    keep_attributes_source = []
    
    base_dataset.import_target_attributes_onsystem(incoming_dataset,
                                                   target_attribute_names, 
                                                   keep_attributes_general, 
                                                   keep_attributes_source, 
                                                   keep_attributes_target)
    
    Parallelsentence2Jcml(base_dataset).write_to_file(output_filename)
    
    
