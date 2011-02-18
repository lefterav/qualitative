#!/usr/bin/env python

# Copyright (c) 2009-2010 Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import protocol
from twisted.internet import reactor
import re


class MyPP(protocol.ProcessProtocol):
    def __init__(self, verses):
        self.verses = verses
        self.data = ""
    def connectionMade(self):
        print "connectionMade!"
        for i in range(self.verses):
            self.transport.write("Aleph-null bottles of beer on the wall,\n" +
                                 "Aleph-null bottles of beer,\n" +
                                 "Take one down and pass it around,\n" +
                                 "Aleph-null bottles of beer on the wall.\n")
        #self.transport.closeStdin() # tell them we're done
    def outReceived(self, data):
        print "outReceived! with %d bytes!" % len(data)
        print "INTEMREDIATE:", self.data
        self.data = self.data + data
    def errReceived(self, data):
        print "errReceived! with %d bytes!" % len(data)
        print data
    def inConnectionLost(self):
        print "inConnectionLost! stdin is closed! (we probably did it)"
    def outConnectionLost(self):
        print "outConnectionLost! The child closed their stdout!"
        # now is the time to examine what they wrote
        print "I saw them write:", self.data
        #(dummy, lines, words, chars, file) = re.split(r'\s+', self.data)
        #print "I saw %s lines" % self.data
    def errConnectionLost(self):
        print "errConnectionLost! The child closed their stderr."
    def processExited(self, reason):
        print "processExited, status %d" % (reason.value.exitCode,)
    def processEnded(self, reason):
        print "processEnded, status %d" % (reason.value.exitCode,)
        print "quitting"
    def onemore(self):
        for i in range(self.verses):
            self.transport.write("Aleph-null bottles of beer on the wall,\n" +
                                 "Aleph-null bottles of beer,\n" +
                                 "Take one down and pass it around,\n" +
                                 "Aleph-null bottles of beer on the wall.\n")
        self.transport.closeStdin() # te

if __name__ == '__main__':
    pp = MyPP(1)
    reactor.spawnProcess(pp, "/usr/bin/java", [ "java", "-jar", "berkeleyParser.jar", "-confidence" , "-kbest", "1" , "-gr", "grammars/eng_sm6.gr"], {}, "/home/elav01/taraxu_tools/berkeleyParser" )
#    reactor.spawnProcess(pp, "wc", ["wc","-l" ], {}, None, None, None, True )
    reactor.run()
    pp.onemore()
    



from SimpleXMLRPCServer import SimpleXMLRPCServer
_baseclass = SimpleXMLRPCServer

class StoppableServer(_baseclass):
    allow_reuse_address = True

    def __init__(self, addr, *args, **kwds):
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









