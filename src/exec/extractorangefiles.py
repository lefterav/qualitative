import ConfigParser
from autoranking import AutoRankingExperiment
import sys

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        #initialize the experiment with the config parameters
        config = ConfigParser.RawConfigParser()
        try:
            print sys.argv[1]
            config.read(sys.argv[1])
            exp = AutoRankingExperiment(config)
            exp.get_files(exp.training_filenames, exp.test_filename)
            #exp.train_decode()
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            