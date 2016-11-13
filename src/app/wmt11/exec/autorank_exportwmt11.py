'''

@author: Eleftherios Avramidis
'''

from autoranking import AutoRankingExperiment
import ConfigParser
import sys

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    try:
        print sys.argv[1]
        config.read(sys.argv[1])
        exp = AutoRankingExperiment(config)
        model = exp.train_classifiers_attributes(exp.training_filenames)
        exp.rank_sax_and_export(exp.test_filename, exp.output_filename, model, exp.output_filename + ".tab", "dfki_parseconf", "de-en", "wmt11combo")

        #exp.train_decode()
    except IOError as (errno, strerror):
        print "configuration file error({0}): {1}".format(errno, strerror)
        sys.exit()