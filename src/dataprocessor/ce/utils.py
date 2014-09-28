from dataprocessor.sax.saxps2jcml import IncrementalJcml
from dataprocessor.ce.cejcml import CEJcmlReader
import logging

def fold_jcml(filename, training_filename, test_filename, batch_size, fold, length=None):
    if not length:
        countreader = CEJcmlReader(filename)
        length = countreader.length()
    reader = CEJcmlReader(filename, all_general=True, all_target=True)
    training_writer = IncrementalJcml(training_filename)
    test_writer = IncrementalJcml(test_filename)
    test_start = len - (batch_size * fold)
    test_end = len - (batch_size * (fold-1))
    
    counter = 0
    for parallelsentence in reader.get_parallelsentences():
        if counter >= test_start or counter < test_end:
            test_writer.add_parallelsentence(parallelsentence)
        else:
            training_writer.add_parallelsentence(parallelsentence)
        
        counter+=1
        
    training_writer.close()
    test_writer.close()
        
    
    
    

def join_jcml(filenames, output_filename, compact=False):
    writer = IncrementalJcml(output_filename)
    for filename in filenames:
        reader = CEJcmlReader(filename, all_general=True, all_target=True)
        for parallelsentence in reader.get_parallelsentences(compact=True):
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
    logging.info("Left {} out of {}".format(count, everything))
    writer.close()
    
    
def join_filter_jcml(filenames, output_filename, callback, **kwargs):
    writer = IncrementalJcml(output_filename)
    count = 0
    everything = 0
    for filename in filenames:
        logging.info("Filtering and joining filename {}".format(filename))
        reader = CEJcmlReader(filename, all_general=True, all_target=True)
        for parallelsentence in reader.get_parallelsentences():
            everything+=1
            if callback(parallelsentence, **kwargs):
                writer.add_parallelsentence(parallelsentence)
                count+=1
    logging.info("Left {} out of {}".format(count, everything))
    writer.close()
    return count, everything
