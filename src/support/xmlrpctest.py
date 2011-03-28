from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor, stdio
from twisted.protocols import basic
import sys
import base64


   

class Shell(basic.LineReceiver):
    from os import linesep as delimiter

    def __init__(self, proxy):
        self.proxy = proxy
       
    def connectionMade(self):
        self.transport.write('>>> ')

    def printValue(self, value):
        print repr(value)
        # go to command line again
        self.transport.write('\n')
        self.transport.write('>>> ')

    def printError(self, error):
        print 'error', error
        # go to command line again
        self.transport.write('\n')
        self.transport.write('>>> ')

    def lineReceived(self, line):
        args = []
        tline = line.replace(')','').replace(';','').replace('\'','')
        m = tline.split('(')
        method = m.pop(0)
        args = m[0].split(',')
        for arg in args:
            arg = base64.standard_b64encode(arg)
        
       
        self.proxy.callRemote(method,*args).addCallbacks(self.printValue, self.printError)
        self.sendLine('Echo: ' + line)
       



if len(sys.argv)==2:
    proxy = Proxy(sys.argv[1])
    stdio.StandardIO(Shell(proxy))

    reactor.run()
else:
    print " Usage : %s proxyURL " % sys.argv[0]
    