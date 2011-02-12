#!/fs/clip-ssmt2/nmadnani/python2.5_64/bin/python2.5

from SimpleXMLRPCServer import SimpleXMLRPCServer
import srilm, sys

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
        return srilm.getUnigramProb(self.lm, s)

    def getBigramProb(self, s):
        return srilm.getBigramProb(self.lm, s)

    def getTrigramProb(self, s):
        return srilm.getTrigramProb(self.lm, s)

    def getSentenceProb(self, s, n):
        import base64
        s = base64.standard_b64decode(s)
        return srilm.getSentenceProb(self.lm, s, n)

    def getCorpusProb(self, filename):
        return srilm.getCorpusProb(self.lm, filename)

    def getCorpusPpl(self, filename):
        return srilm.getCorpusPpl(self.lm, filename)    

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

# Start the server
server.serve_forever()
