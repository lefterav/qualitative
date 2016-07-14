from dataprocessor.sax.saxps2jcml import IncrementalJcml
from dataprocessor.ce.cejcml import CEJcmlReader
from dataprocessor.input.jcmlreader import JcmlReader

import logging
import subprocess
from sentence.pairwisedataset import FilteredPairwiseDataset,\
    AnalyticPairwiseDataset
from sentence.dataset import DataSet
import os
from time import sleep

        
def fold_jcml_cache(self, cache_path, langpair, filename, training_filename, test_filename, repetitions, fold, length=None, clean_testset=True):
    
    # this is the pattern that the file should follow
    data_relativepath = "base_{}.lang_{}.rep_{}.clean_{}".format(os.path.basename(filename), langpair, repetitions, clean_testset)
    data_fullpath = os.path.join(cache_path, data_relativepath)
    
    # create dir if it does not exist
    if not os.path.exists(data_fullpath):
        os.makedirs(data_fullpath)
    
    cached_training_filename = os.path.join(data_fullpath, "{}.trainset.jcml".format(fold))
    cached_test_filename = os.path.join(data_fullpath, "{}.testset.jcml".format(fold))
    
    workingfilename = os.path.join(data_fullpath, "_WORKING")
    wasworking = False
    
    # check whether another process is preparing the files
    while os.path.isfile(workingfilename):
        wasworking = True
        logging.info("Another process is processing the requested cross-validation. Waiting for two minutes")
        sleep(120)
    
    # if the files are not there, prepare them
    if not os.path.isfile(cached_training_filename) and os.path.isfile(cached_test_filename) and wasworking:
        raise Exception("The other process failed to create cross validation")
    
    if not os.path.isfile(cached_training_filename) and os.path.isfile(cached_test_filename):
        logging.info("Cached cross-validation not found. Proceeding with creating it.")
        open(workingfilename, 'a').close()
        fold_jcml_respect_ids(filename, cached_training_filename, cached_test_filename, repetitions, fold, length, clean_testset)
        os.uname(workingfilename)    
        logging.info("Cross-validation created.")
        
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
    
def fold_jcml_respect_ids(filename, training_filename, test_filename, repetitions, fold, length=None, clean_testset=True):
    """
    An incremental function for cross validation. The function is designed to be executed once for every fold. 
    The current fold is passed as a parameter, so the given xml file is read in a memory efficient way (entry by entry)
    and then every entry is entered in the training or the testing part accordingly 
    """
    if repetitions < 2:
        raise SystemExit("{}-fold cross validation does not make sense. Use at least 2 repetitions.".format(repetitions))
    
    if not length:
        #quickest way of getting the length of the file, without parsing its xml
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
    
    logging.info("Test set for fold {} will be between HITs {} and {} (size: {})".format(fold, test_start, test_end-1, test_end-test_start))
    
    counter = 0
    
    #get one by one the sentences incrementally, batch them per id and put
    #them in the suitable set
    parallelsentences_per_id = []
    previous_sentence_id = None
    totalsentences = 0
    test_size = 0
    merged_test_size = 0 
    train_size = 0

    for parallelsentence in reader.get_parallelsentences():
        sentence_id = parallelsentence.get_fileid_tuple()
        
        (parallelsentence.attributes.setdefault("testset", None), parallelsentence.get_id())

        # collect judgments of the same sentence until a new sentence appears
        # (we suppose that the original corpus has been ordered by sentence id)
        
        # if a new sentence appears, flush
        if previous_sentence_id != None and sentence_id != previous_sentence_id:
            train_count, test_count, merged_test_count = _flush_per_id(parallelsentences_per_id, training_writer, test_writer, 
                                                    counter, test_start, test_end, clean_testset)
            totalsentences += len(parallelsentences_per_id)
            train_size += train_count
            test_size += test_count
            merged_test_size += merged_test_count
            parallelsentences_per_id = []
        
        parallelsentences_per_id.append(parallelsentence)
        previous_sentence_id = sentence_id
        counter+=1
        
    train_count, test_count = _flush_per_id(parallelsentences_per_id, training_writer, test_writer, 
                                            counter, test_start, test_end, clean_testset)
    totalsentences += len(parallelsentences_per_id)
    train_size += train_count
    test_size += test_count
    
    if test_size != batch_size:
        logging.info("Fold {} will have an actual number of {} test sentences  instead of {}".format(fold, test_size, batch_size))
    if merged_test_count != test_size:
        logging.info("Fold {} aggregated {} test sentences to {}".format(fold, test_size, merged_test_count))
    training_writer.close()
    test_writer.close()
    
        
def _flush_per_id(parallelsentences_per_id, training_writer, test_writer, counter, test_start, test_end, clean_testset):
    if counter < test_start or counter >= test_end:
        training_writer.add_parallelsentences(parallelsentences_per_id)
        return len(parallelsentences_per_id), 0, 0
    else:
        if not clean_testset:
            test_writer.add_parallelsentences(parallelsentences_per_id)
            count = len(parallelsentences_per_id)
            return 0, count, count
        else:
            dataset = DataSet(parallelsentences_per_id)
            analytic_dataset = AnalyticPairwiseDataset(dataset) 
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
        file_id = filename.replace("-jcml-rank.all.analyzed.f.jcml", "")
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
