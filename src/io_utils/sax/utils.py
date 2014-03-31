from io_utils.sax.saxps2jcml import IncrementalJcml
from io_utils.sax.cejcml import CEJcmlReader
import logging as log

def join_jcml(filenames, output_filename):
    writer = IncrementalJcml(output_filename)
    for filename in filenames:
        reader = CEJcmlReader(filename, all_general=True, all_target=True)
        for parallelsentence in reader.get_parallelsentences():
            writer.add_parallelsentence(parallelsentence)

    writer.close()

def filter_jcml(input_filename, output_filename, callback, **kwargs):
    reader = CEJcmlReader(input_filename, all_general=True, all_target=True)
    writer = IncrementalJcml(output_filename)
    count = 0
    everything = 0
    for parallelsentence in reader.get_parallelsentences():
        everything+=1
        if callback(parallelsentence, **kwargs):
            writer.add_parallelsentence(parallelsentence)
            count+=1
    log.info("Left {} out of {}".format(count, everything))
    writer.close()
    
    
def join_filter_jcml(filenames, output_filename, callback, **kwargs):
    writer = IncrementalJcml(output_filename)
    count = 0
    everything = 0
    for filename in filenames:
        reader = CEJcmlReader(input_filename, all_general=True, all_target=True)
        for parallelsentence in reader.get_parallelsentences():
            everything+=1
            if callback(parallelsentence, **kwargs):
                writer.add_parallelsentence(parallelsentence)
                count+=1
    log.info("Left {} out of {}".format(count, everything))
    writer.close()
