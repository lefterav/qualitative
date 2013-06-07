'''
Created on Jun 7, 2013

@author: dupo
'''
import sys
from io_utils.input.jcmlreader import JcmlReader
from io_utils.sax.saxps2jcml import Parallelsentence2Jcml


if __name__ == '__main__':
    target_attribute_names = [sys.argv[1]]
    base_xml_filename = sys.argv[2]
    incoming_xml_filename = sys.argv[3]
    output_filename = sys.argv[4]
    
    base_dataset = JcmlReader(base_xml_filename).get_dataset()
    incoming_dataset = JcmlReader(incoming_xml_filename).get_dataset()
    
    keep_attributes_general = ["judgement_id","langsrc","testset","id","langtgt"]
    keep_attributes_source = []
    keep_attributes_target = ['system','rank',]
    
    base_dataset.import_target_attributes_onsystem(incoming_dataset,
                                                   target_attribute_names, 
                                                   keep_attributes_general, 
                                                   keep_attributes_source, 
                                                   keep_attributes_target)
    
    Parallelsentence2Jcml(base_dataset).write_to_file(output_filename)
    
    