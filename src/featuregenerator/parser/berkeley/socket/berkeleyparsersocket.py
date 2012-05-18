'''
Created on Sep 21, 2011

@author: jogin
'''

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient
from py4j.java_gateway import java_import

 #@UnresolvedImport

import subprocess
import time
import os
import sys
import random


class BerkeleyParserSocket():
    """
    A flexible wrapper for the Berkeley parser. It starts the Berkeley parser as an object
    which can be called as a Python object. It requires presence of external java libraries.
    The advantage of this class (e.g. vs XMLRPC) is that it can fully control starting and 
    stopping the parsing engine within Python code.   
    """
    
#    def __init__(self, grammarfile, classpath):
    def __init__(self, grammarfile, gateway):
        """
        @param berkeley_parser_jar: Location of BerkeleyParser.jar; a modified java library that
        fetches full parsing details from the Berkeley Engine and calculates full features upon request
        @type berkeley_parser_jar: string
        @param py4j_jar: Location of py4j.jar; java library responsible for connecting to java from python
        through a socket connection.
        @type py4j_jar: string
        @param java_server_loc: Location of JavaServer.class
        @type java_server_loc: string
        
        Example use
        
        grammarfile = "/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr"
        berkleyjar = "/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar"
        py4jjar = "/usr/share/py4j/py4j0.7.jar"
        bps = BerkeleyParserSocket(grammarfile, berkleyjar, py4jjar)
        print bps.parse("This is a sentence")
        bps.close() #optional, but better to do
        
        """
        self.grammarfile = grammarfile
        
#        print "initializing Berkeley client"
##        try:
#        # connect to the JVM
#        classpath, dir_path = classpath
#
#        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
#        subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % dir_path])
#        
#        # prepare and run Java server
#        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
#        cmd = ["java", "-cp", classpath, "JavaServer" ]
#        cmd = " ".join(cmd)
#        
#        self.jvm = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE) #shell=True,
#        self.jvm.stdout.flush()
#        socket_no = int(self.jvm.stdout.readline().strip())
#        sys.stderr.write("Received socket number {0} from Java Server".format(socket_no))
#        self.socket = GatewayClient('localhost', socket_no)
#        sys.stderr.write("Started java process with pid {} in socket {}".format(self.jvm.pid, socket_no))
#        
#        gateway = JavaGateway(self.socket)
        
        module_view = gateway.new_jvm_view()
        
        java_import(module_view, 'BParser')
    
        
        # get the application instance
        self.bp_obj =  module_view.BParser(grammarfile)
        print "got BParser object"
#        except:
#            self._reconnect(berkeley_parser_jar, py4j_jar)
    
    def _reconnect(self, berkeley_parser_jar, py4j_jar):
        #define running directory
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        subprocess.check_call(["javac", "-classpath", "%s:%s:%s" % (berkeley_parser_jar, py4j_jar, dir_path), "%s/JavaServer.java" % dir_path])
        
        
        # prepare and run Java server
        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
        cmd = ["java", "-cp", "%s:%s:%s" % (self.berkeley_parser_jar, py4j_jar, dir_path), "JavaServer" ]
        self.process = subprocess.Popen(cmd,  close_fds=True) #shell=True,
        sys.stderr.write("Started java process with pid %d\n" % self.process.pid)
        
        # wait so that server starts
        time.sleep(2)
        self.gateway = JavaGateway()
        bpInstance = self.gateway.entry_point
    
        # call the method get_BP_obj() in java
        self.bp_obj = bpInstance.get_BP_obj(self.grammarfile)

    def parse(self, sentence_string):
        """
        It calls the parse function on BParser object.
        """
         
        # call the python function parse() on BParser object
        try:
            parseresult = self.bp_obj.parse(sentence_string)
        except:
            self._reconnect(self.berkeley_parser_jar, self.py4_jar)
            parseresult = self.bp_obj.parse(sentence_string)
        return parseresult
        
#    def __del__(self):
#        self.jvm.terminate()
#    
#    def __del__(self):
#        self.gateway.deluser()
#        
#        if self.gateway.getusers() == 0:
#            self.gateway.shutdown()
#            try:
#                self.process.terminate()
#            except:
#                pass
        
            
#    def __del__(self):
#        """
#        Java server is terminated from here.
#        """
#        self.bp_obj = None
        

        
#    def __del__(self):
#        """
#        Destroy object when object unloaded or program exited
#        """
#        self.gateway.shutdown()
#        #sys.stderr.write( "trying to close process %d\n" % self.process.pid)
#        self.process.terminate()
        



#bps = BerkeleyParserSocket("/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr", "/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar")
#bps2 = BerkeleyParserSocket("/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr", "/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar")
#print bps2.parse("This is a sentence")
#bps2.close()
#print bps.parse("This is another sentence")
#bps.close()




