from preprocess_glassbox import extract_glassbox_features_moses
import os, sys
import logging

if __name__ == '__main__':
    #print db.retrieve_uid("Deutsch", ['069592001_cust1-069592001-2'])
    source_filename = os.path.expanduser("/share/taraxu/evaluation-rounds/r2/test-data/wmt11/wmt11.de-en.en")
    ids_filename = os.path.expanduser("/share/taraxu/evaluation-rounds/r2/test-data/wmt11/wmt11.de-en.en.links")
    target_filename = os.path.expanduser("/share/taraxu/evaluation-rounds/r2/system-outputs/moses/en-de/wmt11.truecased.3.dehp.detok")
    log_filename = os.path.expanduser("/share/taraxu/evaluation-rounds/r2/logs/en-de/moses/wmt11.v2.log.3")
    testset_type = "wmt11"
<<<<<<< .merge_file_SjB4NV
    output_filename = os.path.expanduser("~/wmt11.moses.gb.jcml")
    source_lang = "en"
    target_lang = "de"
=======
    output_filename = sys.argv[1]
#    output_filename = os.path.expanduser("/wmt11.moses.gb.jcml")
    source_lang = "de"
    target_lang = "en"
>>>>>>> .merge_file_JhX9x1

    sth = logging.StreamHandler()
    sth.setLevel(logging.DEBUG)

    extract_glassbox_features_moses(source_filename, ids_filename, testset_type, target_filename, log_filename, output_filename, source_lang, target_lang, backoff_reference=True)
