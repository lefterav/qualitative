#!/fs/clip-ssmt2/nmadnani/python2.5_64/bin/python2.5

from SimpleXMLRPCServer import SimpleXMLRPCServer
import srilm
import sys
#import base64


_baseclass = SimpleXMLRPCServer
class StoppableServer(_baseclass):
    allow_reuse_address = True

    def __init__(self, addr, lm, *args, **kwds):
        self.myhost, self.myport = addr
	self.lm = lm
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
	srilm.deleteLM(self.lm)
	return 0, "Server terminated on host %r, port %r" % (self.myhost, self.myport)


class LM:

    def __init__(self, lm):
	self.lm = lm

    def howManyNgrams(self, type):
        return srilm.howManyNgrams(self.lm, type)

    def getUnigramProb(self, s):
        s = codecs.encode(s, "utf-8")
        return srilm.getUnigramProb(self.lm, s)

    def getBigramProb(self, s):
        s = codecs.encode(s, "utf-8")
        return srilm.getBigramProb(self.lm, s)

    def getTrigramProb(self, s):
        s = codecs.encode(s, "utf-8")
        return srilm.getTrigramProb(self.lm, s)

    def getSentenceProb(self, s, n=None ):
        s = codecs.encode(s, "utf-8")
        if not n:
            n = len(s.split(' '))
        return srilm.getSentenceProb(self.lm, s, n)

    def getCorpusProb(self, filename):
        return srilm.getCorpusProb(self.lm, filename)

    def getCorpusPpl(self, filename):
        return srilm.getCorpusPpl(self.lm, filename)
    
    def getNgramFeatures_batch(self, batch):
        features_batch = []
        for row in batch:
            features_row = []
            for tokens in row:
                features_row.append(self.getNgramFeatures_string(tokens))
            features_batch.append(features_row)
        return features_batch                
            
    
    def getNgramFeatures_string(self, tokens):
        unk_count = 0
        uni_probs = 1
        bi_probs = 1
        tri_probs = 1
        unk_tokens = []
        
        #for i in range(len(tokens)):
        #    tokens[i] = base64.standard_b64decode(tokens[i])
        
        #check for unknown words and collect unigram probabilities:
        for token in tokens:
            try: 
                uni_prob = self.getUnigramProb(token)
                #uni_prob = self.getUnigramProb(base64.standard_b64encode(token))
                if uni_prob == -99:
                    unk_count += 1
                    unk_tokens.append(token)
                    sys.stderr.write("Unknown word: %s\n" % token)
                else:
                    uni_probs += uni_prob
            except: 
                sys.stderr.write("Failed to retrieve unigram probability for token: '%s'\n" % token) 
                pass
        
        
        #get bigram probabilities
        for pos in range ( len(tokens) -1 ):
            token = tokens[pos:pos+2]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens):
                try:
                    bi_prob = self.getBigramProb(' '.join(token))
                    #bi_prob = self.getBigramProb(base64.standard_b64encode(' '.join(token)))
                    bi_probs += bi_prob
                except:
                    sys.stderr.write("Failed to retrieve bigram probability for tokens: '%s'\n" % ' '.join(token)) 

         
        #get trigram probabilities
        for pos in range ( len(tokens) -2 ):
            token = tokens[pos:pos+3]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens) and (token[2] not in unk_tokens):
                try:
                    tri_prob = self.getTrigramProb(' '.join(token))
                    #tri_prob = self.getTrigramProb(base64.standard_b64encode(' '.join(token)))
                    tri_probs += tri_prob
                except:
                    sys.stderr.write("Failed to retrieve trigram probability for tokens: '%s'\n" % ' '.join(token)) 
        
        sent_string = " ".join(tokens)
        prob = str(self.getSentenceProb(sent_string), len(tokens))
        #prob = str(str (self.getSentenceProb(base64.standard_b64encode(sent_string), len(tokens))))
        
        attributes = { 'unk' : str(unk_count),
                       'uni-prob' : str(uni_probs),
                       'bi-prob' : str(bi_probs),
                       'tri-prob' : str(tri_probs), 
                       'prob' : str(prob) }
        return attributes
          

# Get command line arguments
args = sys.argv[1:]
if len(args) != 1:
    sys.stderr.write('Usage: lmserver.py <configfile>\n')
    sys.exit(1)
else:
    configfile = open(args[0],'r')

# Initialize all needed variables to None
address = None
port = None
lmfilename = None
lmorder = None

# Source the config file
exec(configfile)

# Make sure all needed variables got set properly
missing = []
for var in ['address', 'port', 'lmfilename', 'lmorder']:
    if eval(var) is None:
        missing.append(var)
if missing:
    sys.stderr.write('The following options are missing in the configuration file: %s\n' % ', '.join(missing))
    sys.exit(1)

# Initialize the LM data structure 
lmstruct = srilm.initLM(lmorder)

# Read the LM file into this data structure
try:
    srilm.readLM(lmstruct, lmfilename)
except:
    sys.stderr.write('Error: Could not read LM file\n')
    sys.exit(1)

# Create a server that is built on top of this LM data structure
try:
    server = StoppableServer((address, port), lmstruct, logRequests = False)
    
except:
    sys.stderr.write('Error: Could not create server\n')
    sys.exit(1)

# Create a wrapper around this data structure that exposes all the functions
# as methods
lm = LM(lmstruct)

# Register introspection functions with the server
server.register_introspection_functions()

# Register the LM wrapper instance with the server 
server.register_instance(lm)
sys.stderr.write('Server ready\n')

# Start the server
server.serve_forever()
