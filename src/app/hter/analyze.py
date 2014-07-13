import logging as log
import sys
from io_utils.sax.utils import join_jcml
from io_utils.ce.cejcml import CEJcmlStats
from io_utils.input.jcmlreader import JcmlReader

if __name__ == '__main__':
    #logging
    log.basicConfig(level=log.INFO)
    
    #load and join filenames
    log.info("Creating joined file")
    input_filenames = sys.argv[1:]
    print "Input filenames:", input_filenames
    input_xml_filename = "train.jcml"
    join_jcml(input_filenames, input_xml_filename)
    
    #list attributes


    
    print
    
    print CEJcmlStats(input_xml_filename, all_general=True, all_target=True).get_attribute_statistics()
