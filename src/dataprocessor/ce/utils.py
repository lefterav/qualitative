from dataprocessor.sax.saxps2jcml import IncrementalJcml
from dataprocessor.ce.cejcml import CEJcmlReader
import logging
import subprocess

def fold_jcml(filename, training_filename, test_filename, repetitions, fold, length=None):
    
    if repetitions < 2:
        raise SystemExit('%i-fold cross validation does not make sense. Use at least 2 repetitions.'%repetitions)
    
    if not length:
        length = int(subprocess.check_output(["grep", "-c", "<judgedsentence", filename]).strip())
        logging.info("Dataset has {} entries".format(length))
    
    #get how big each batch should be
    batch_size = length // repetitions
    
    if batch_size == 0:
            raise SystemExit('Too many repetitions for cross-validation with this dataset. Max. number of repetitions is {}.'.format(length))
    
    #create one reader and two writers (for training and test set respectively)    
    reader = CEJcmlReader(filename, all_general=True, all_target=True)
    training_writer = IncrementalJcml(training_filename)
    test_writer = IncrementalJcml(test_filename)
    
    #define where is the beginning and the end of the test set
    test_start = length - (batch_size * (fold+1))
    test_end = length - (batch_size * fold)
    
    #increase the last fold so as to contain all sentences remaining
    if fold == repetitions-1:
        test_start = 0 
    
    logging.info("Test set for fold {} will be between sentences {} and {}".format(fold, test_start, test_end))
    
    counter = 0
    
    #get one by one the sentences incrementally and put
    #them in the suitable set
    for parallelsentence in reader.get_parallelsentences():
        if counter < test_start or counter >= test_end:
            training_writer.add_parallelsentence(parallelsentence)
        else:
            test_writer.add_parallelsentence(parallelsentence)
        counter+=1
        
    training_writer.close()
    test_writer.close()
    
    
def fold_jcml_respect_ids(filename, training_filename, test_filename, repetitions, fold, length=None):
    
    if repetitions < 2:
        raise SystemExit('%i-fold cross validation does not make sense. Use at least 2 repetitions.'%repetitions)
    
    if not length:
        length = int(subprocess.check_output(["grep", "-c", "<judgedsentence", filename]).strip())
        logging.info("Dataset has {} entries".format(length))
    
    #get how big each batch should be
    batch_size = length // repetitions
    
    if batch_size == 0:
            raise SystemExit('Too many repetitions for cross-validation with this dataset. Max. number of repetitions is {}.'.format(length))
    
    #create one reader and two writers (for training and test set respectively)    
    reader = CEJcmlReader(filename, all_general=True, all_target=True)
    training_writer = IncrementalJcml(training_filename)
    test_writer = IncrementalJcml(test_filename)
    
    #define where is the beginning and the end of the test set
    test_start = length - (batch_size * (fold+1))
    test_end = length - (batch_size * fold)
    
    #increase the last fold so as to contain all sentences remaining
    if fold == repetitions-1:
        test_start = 0 
    
    logging.info("Test set for fold {} will be between sentences {} and {}".format(fold, test_start, test_end))
    
    counter = 0
    
    #get one by one the sentences incrementally, batch them per id and put
    #them in the suitable set
    parallelsentences_per_id = []
    previous_sentence_id = None
    for parallelsentence in reader.get_parallelsentences():
        sentence_id =  "{}:{}".format(parallelsentence.attributes["testset"], parallelsentence.attributes["id"])

        #sentence_id = parallelsentence.get_compact_id()
        if previous_sentence_id != None and sentence_id != previous_sentence_id:
            logging.info("Fold {} will have an actual number of sentences {} instead of {}".format(fold, len(parallelsentences_per_id), batch_size))
            _flush_per_id(parallelsentences_per_id, training_writer, test_writer, counter, test_start, test_end)
            parallelsentences_per_id = []
        
        parallelsentences_per_id.append(parallelsentence)
        previous_sentence_id = sentence_id
        counter+=1
        
    _flush_per_id(parallelsentences_per_id, training_writer, test_writer, counter, test_start, test_end)

    training_writer.close()
    test_writer.close()
        
def _flush_per_id(parallelsentences_per_id, training_writer, test_writer, counter, test_start, test_end):
    if counter < test_start or counter >= test_end:
        for parallelsentence in parallelsentences_per_id:
            training_writer.add_parallelsentence(parallelsentence)
    else:
        for parallelsentence in parallelsentences_per_id:
            test_writer.add_parallelsentence(parallelsentence)


def join_jcml(filenames, output_filename, compact=False):
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
