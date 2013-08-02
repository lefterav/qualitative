#!/fs/clip-ssmt2/nmadnani/python2.5_64/bin/python2.5

from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import codecs
from types import *
#import base64
import unicodedata


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
