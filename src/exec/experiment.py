import sys
import ConfigParser



class Experiment():
    """
    Organizes the main experiment process concerning 
    selection/ranking of multiple systems' output, given
    a configuration file and contained experiment-specific functions
    """
    def __init__(self, configfile):
        """
        Initializes the experiment class, by storing the parsed config parameters
        @param config: the full system path to a configuration file 
        @type config: String
        """
        self.config = ConfigParser.RawConfigParser()
        try:
            self.config.read(configfile)
        except IOError as (errno, strerror):
            print "configuration file error({0}): {1}".format(errno, strerror)
            sys.exit()
            
    def launch(self):
        for section in self.config.sections():
            if not section == "general":
                function = getattr(self, self.config.get(section, "function"))
                function(section)
    
    def train_classifiers(self):
        """
        It handles the training of specific classifiers given specific attributes
        @return a list of classifiers
        """
        
        
        
                

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'USAGE: %s configuration_file.cfg' % sys.argv[0]
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        #initialize the experiment with the config parameters
        experiment = Experiment(sys.argv[1])
        
    
    