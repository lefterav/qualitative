from dataprocessor.sax.saxps2jcml import IncrementalJcml
from dataprocessor.ce.cejcml import CEJcmlReader
from dataprocessor.input.jcmlreader import JcmlReader

import logging
import subprocess
import os
from sentence.pairwisedataset import FilteredPairwiseDataset,\
    AnalyticPairwiseDataset
from sentence.dataset import DataSet
import os
from time import sleep
from random import randint
from copy import deepcopy


def get_length_jcml(filename):
    try:
        return int(subprocess.check_output(["grep", "-c", "<judgedsentence", filename]).strip())
    except:
        return -1 

def join_or_link_jcml(source_path, source_datasets, ready_dataset):
    """
    Create a joined file from the given datasets if needed,
    or link them if they have already been given as one file
    """

    #get full path for all files
    source_datasets = [os.path.join(source_path, f) for f in source_datasets]
    logging.info("Source datasets: {}".format(source_datasets))
    if len(source_datasets)==1:
        logging.debug("Linking {} to {}".format(source_datasets[0], ready_dataset))
        logging.debug(os.listdir(os.curdir))
        try:
            os.symlink(source_datasets[0], ready_dataset)
        except OSError as e:
            if '[Errno 17]' in str(e):
                logging.warn("Could not create symlink for data. [Errno 17] File exists")
            else:
                raise Exception(e)
        
        
    else:
        logging.info("Joining training files")
        join_jcml(source_datasets, ready_dataset)


        
def fold_jcml_cache(cache_path, langpair, filepath, filenames, training_filename, 
        test_filename, repetitions, fold, length=None, clean_testset=True):

    # this is the pattern that the file should follow
    data_relativepath = "base_{}_{}.lang_{}.rep_{}.clean_{}".format(os.path.basename(filepath),
            "_".join(filenames), langpair, repetitions, clean_testset)
    data_fullpath = os.path.join(cache_path, data_relativepath)

    joined_filename = os.path.join(data_fullpath, "{}.dataset.jcml".format(fold))

    sleep(randint(0,60))
    if fold > 0:
        sleep(2)

    # create dir if it does not exist
    if not os.path.exists(data_fullpath):
        os.makedirs(data_fullpath)
 
    if not os.path.exists(joined_filename):
        logging.debug("join_or_link_jcml {},{},{}".format(filepath, filenames, joined_filename))
        join_or_link_jcml(filepath, filenames, joined_filename)
   
    cached_training_filename = os.path.join(data_fullpath, "{}.trainset.jcml".format(fold))
    cached_test_filename = os.path.join(data_fullpath, "{}.testset.jcml".format(fold))
    
    workingfilename = os.path.join(data_fullpath, "{}.WORKING".format(fold))
    wasworking = False
    
   
    # if the files are not there, prepare them
    #if wasworking and \
    #    not (os.path.isfile(cached_training_filename) and os.path.isfile(cached_test_filename)):            
    #    raise Exception("The other process failed to create cross validation")
 
    training_file_exists = get_length_jcml(cached_training_filename) > 0
    test_file_exists = get_length_jcml(cached_test_filename) > 0
   
    # check whether another process is preparing the files
    while os.path.isfile(workingfilename):
        wasworking = True
        logging.info("Another process is processing the requested cross-validation. Waiting for two minutes")
        sleep(120)
    
    if not training_file_exists or not test_file_exists:
        open(workingfilename, 'a').close()
        logging.info("Cached cross-validation for fold {} not found. Proceeding with creating it.".format(fold))
        fold_jcml_respect_ids(joined_filename, cached_training_filename, cached_test_filename, 
            repetitions, fold, length, clean_testset)
        os.unlink(workingfilename)    
        logging.info("Cross-validation created.")

    if not (os.path.isfile(cached_training_filename) and os.path.isfile(cached_test_filename)):            
        raise Exception("Our process failed to create cross validation")
        
    try:
        os.link(cached_training_filename, training_filename)
    except:
        logging.warn("Training file cannot be linked from cache: {}".format(cached_training_filename))
    
    try:
        os.link(cached_test_filename, test_filename)
    except:
        logging.warn("Test file cannot be linked from cache: {}".format(cached_test_filename))
        

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

def get_clean_testset(input_file, output_file):
    plain_dataset = JcmlReader(input_file).get_dataset()
#    plain_dataset.remove_ties()
    analytic_dataset = AnalyticPairwiseDataset(plain_dataset) 
    filtered_dataset = FilteredPairwiseDataset(analytic_dataset, 1.00)
    filtered_dataset.remove_ties()
    reconstructed_dataset = filtered_dataset.get_multiclass_set()
    reconstructed_dataset.remove_ties()
    IncrementalJcml(output_file).add_parallelsentences(reconstructed_dataset.get_parallelsentences())

def fold_jcml_respect_ids(filename, training_filename, test_filename, 
                     repetitions, fold, length=None, clean_testset=True):
    
                     
    fold_respect_ids(CEJcmlReader(filename, all_general=True, all_target=True), 
                     IncrementalJcml(training_filename), IncrementalJcml(test_filename), 
                     repetitions, fold, length, clean_testset)
    

def fold_respect_ids(reader, training_writer, test_writer, repetitions, fold, length=None, clean_testset=True):
    """
    An incremental function for cross validation. The function is designed to be executed once for every fold. 
    The current fold is passed as a parameter, so the given xml file is read in a memory efficient way (entry by entry)
    and then every entry is entered in the training or the testing part accordingly 
    """
    if repetitions < 2:
        raise SystemExit("{}-fold cross validation does not make sense. Use at least 2 repetitions.".format(repetitions))
    
    if not length:
        length = len(reader)
        
    #get how big each batch should be
    batch_size = length // repetitions
    
    if batch_size == 0:
        raise SystemExit('Too many repetitions for cross-validation with this dataset. Max. number of repetitions is {}.'.format(length))
        
    #define where is the beginning and the end of the test set
    test_start = length - (batch_size * (fold+1))
    test_end = length - (batch_size * fold)
    
    #increase the last fold so as to contain all sentences remaining
    if fold == repetitions-1:
        test_start = 0 
    
    logging.info("Test set for fold {} will be between HITs {} and {} (size: {})".format(
        fold, test_start, test_end-1, test_end-test_start))
    
    counter = 0
    
    #get one by one the sentences incrementally, batch them per id and put
    #them in the suitable set
    parallelsentences_per_id = []
    previous_sentence_id = None
    totalsentences = 0
    test_size = 0
    merged_test_size = 0 
    train_size = 0
    
    logging.debug("Data length before loop of fold {}: {}".format(fold, len(reader)))

    for parallelsentence in reader.get_parallelsentences():
        sentence_id = parallelsentence.get_fileid_tuple()
        logging.debug("Data length before loop of sentence_id : {}, {}".format(sentence_id, len(reader)))

        # collect judgments of the same sentence until a new sentence appears
        # (we suppose that the original corpus has been ordered by sentence id)
        
        # if a new sentence appears, flush
        logging.debug("{}, {}".format(counter, sentence_id))
        if previous_sentence_id != None and sentence_id != previous_sentence_id:
            logging.debug("Data length before flushing of sentence_id : {}, {}".format(sentence_id, len(reader)))

            train_count, test_count, merged_test_count = _flush_per_id(parallelsentences_per_id, 
                                                         training_writer, test_writer, counter, 
                                                         test_start, test_end, clean_testset)
            logging.debug("Data length after flushing of sentence_id : {}, {}".format(sentence_id, len(reader)))

            totalsentences += len(parallelsentences_per_id)
            train_size += train_count
            test_size += test_count
            merged_test_size += merged_test_count
            parallelsentences_per_id = []
        
        parallelsentences_per_id.append(deepcopy(parallelsentence))
        previous_sentence_id = sentence_id
        counter+=1
        
        
    train_count, test_count, merged_test_count = _flush_per_id(parallelsentences_per_id, 
                                              training_writer, test_writer, counter, 
                                              test_start, test_end, clean_testset)
    totalsentences += len(parallelsentences_per_id)
    train_size += train_count
    test_size += test_count
    merged_test_size += merged_test_count
    
    if test_size != batch_size:
        logging.info("Fold {} will have an actual number of {} test sentences  instead of {}".format(
            fold, test_size, batch_size))
    if merged_test_count != test_size:
        logging.info("Fold {} aggregated {} test sentences to {}".format(fold, test_size, merged_test_count))
    training_writer.close()
    test_writer.close()
    
        
def _flush_per_id(parallelsentences_per_id, training_writer, test_writer, counter, test_start, 
                  test_end, clean_testset):
    if counter <= test_start or counter > test_end:
        logging.debug("Flushing in training set")
        training_writer.add_parallelsentences(parallelsentences_per_id)
        return len(parallelsentences_per_id), 0, 0
    else:
        if not clean_testset:
            logging.debug("Flushing in normal testset")
            test_writer.add_parallelsentences(parallelsentences_per_id)
            count = len(parallelsentences_per_id)
            return 0, count, count
        else:
            logging.debug("Flushing in clean testset")
            tmpdataset = DataSet(parallelsentences_per_id)
            analytic_dataset = AnalyticPairwiseDataset(tmpdataset)
            tmpdataset = None 
            filtered_dataset = FilteredPairwiseDataset(analytic_dataset, 1.00)
            filtered_dataset.remove_ties()
            reconstructed_dataset = filtered_dataset.get_multiclass_set()
            reconstructed_dataset.remove_ties()
            reconstructed_sentences = reconstructed_dataset.get_parallelsentences()
            test_writer.add_parallelsentences(reconstructed_sentences)
            return 0, len(parallelsentences_per_id), len(reconstructed_sentences)

def join_jcml(filenames, output_filename, compact=False):
    '''
    Join two XML files, by processing them line-by-line to not overload memory
    A file id is added in every sentence, to aid with specifying unique ids
    @param filenames: a list of filenames that need to be joined
    @type filenames: list of strings
    @param output_filename: one filename which will be the result of the joining
    @type output_filename: str
    @param compact: whether the XML should be stripped of the strings
    @type compact: boolean
    '''
    #initialize the incremental writer
    writer = IncrementalJcml(output_filename)
    #iterate over all files
    for filename in filenames:
        #remove commond file ending for WMT files from the file id
        file_id = os.path.basename(filename).replace("-jcml-rank.all.analyzed.f.jcml", "")
        reader = CEJcmlReader(filename, all_general=True, all_target=True)
        #iterate over all incoming sentences
        for parallelsentence in reader.get_parallelsentences():
            parallelsentence.attributes["file_id"] = file_id
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
