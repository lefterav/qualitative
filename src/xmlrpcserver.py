#!/fs/clip-ssmt2/nmadnani/python2.5_64/bin/python2.5

from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import codecs
from types import *
#import base64
import unicodedata
import cPickle as pickle
from sentence.sentence import SimpleSentence

from ml.lib.orange import OrangeRuntimeRanker 
from sentence.parallelsentence import ParallelSentence

from ml.lib import orange

_baseclass = SimpleXMLRPCServer
class StoppableServer(_baseclass):
    allow_reuse_address = True

    def __init__(self, addr, lm, *args, **kwds):
        self.myhost, self.myport = addr
        _baseclass.__init__(self, addr, *args, **kwds)
        self.register_function(self.stop_server)
        self.quit = False

    def serve_forever(self):
        while not self.quit:
            try:
                self.handle_request()
            except KeyboardInterrupt:
                break
        self.server_close()

    def stop_server(self):
        self.quit = True
        return 0, "Server terminated on host %r, port %r" % (self.myhost, self.myport)




class Autoranking:

    def __init__(self, featuregenerators, attset, classifiername):
        self.featuregenerators = featuregenerators
        self.attset = attset
        self.ranker = OrangeRuntimeRanker(classifiername)
        
    def rank(self, source, translations):
        sourcesentence = SimpleSentence(source)
        translationsentences = [SimpleSentence(t) for t in translations]
        parallelsentence = ParallelSentence(sourcesentence, translationsentences)
        
        #annotate the parallelsentence
        annotated_parallelsentence = self._annotate(parallelsentence)
        ranking = self.ranker.rank_sentence(annotated_parallelsentence)
        
        
        return ranking
        
    def _annotate(self, parallelsentence):
        for featuregenerator in self.featuregenerators:
            parallelsentence = featuregenerator.add_features_parallelsentence(parallelsentence)
        return parallelsentence
    

if __name__ == "__main__":
    
    classifier_filename = "/share/taraxu/selection-mechanism/wmt13/sentenceranking/autoranking_wmt13_newfeatures1_de_en/class_nameranklangpairde-eninclude_references0.0ties0.0trainset_modeannotatedattattset_24classifierLogReg/classifier.clsf"
    
    
    source = "Wir müssen diese Lösung diskutieren"
    target1 = "We have to discuss this solution"
    target2 = "This solution have we to discuss"
    target3 = "We must this solution discuss"

    autoranker = Autoranking(classifier_filename)
    print autoranker.rank(source, [target1, target2, target3])

# Get command line arguments
# args = sys.argv[1:]
# if len(args) != 1:
#     sys.stderr.write('Usage: lmserver.py <configfile>\n')
#     sys.exit(1)
# else:
#     configfile = open(args[0],'r')
# 
# # Initialize all needed variables to None
# address = None
# port = None
# lmfilename = None
# lmorder = None
# 
# # Source the config file
# exec(configfile)
# 
# # Make sure all needed variables got set properly
# missing = []
# for var in ['address', 'port', 'lmfilename', 'lmorder']:
#     if eval(var) is None:
#         missing.append(var)
# if missing:
#     sys.stderr.write('The following options are missing in the configuration file: %s\n' % ', '.join(missing))
#     sys.exit(1)
# 
# #initialize qualitative
# qualitative = Qualitative()
# 
# # Create a server that is built on top of this LM data structure
# try:
#     server = StoppableServer((address, port))
#     
# except:
#     sys.stderr.write('Error: Could not create server\n')
#     sys.exit(1)
# 
# # Register introspection functions with the server
# server.register_introspection_functions()
# 
# # Register the qualitative instance with the server 
# server.register_instance(qualitative)
# sys.stderr.write('Server ready\n')
# 
# # Start the server
# server.serve_forever()
