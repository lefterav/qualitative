'''
Created on Sep 21, 2011

@author: jogin
'''

from py4j.java_gateway import JavaGateway #@UnresolvedImport

import subprocess
import time
import os
import sys


class BerkeleyParserSocket():
    """
    A flexible wrapper for the Berkeley parser. It starts the Berkeley parser as an object
    which can be called as a Python object. It requires presence of external java libraries.
    The advantage of this class (e.g. vs XMLRPC) is that it can fully control starting and 
    stopping the parsing engine within Python code.   
    """
    def __init__(self, grammarfile, berkeley_parser_jar, py4j_jar):
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
        
        #define running directory
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        subprocess.check_call(["javac", "-classpath", "%s:%s:%s" % (berkeley_parser_jar, py4j_jar, dir_path), "JavaServer.java"])
        
        
        # prepare and run Java server
        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
        cmd = ["java", "-cp", "%s:%s:%s" % (berkeley_parser_jar, py4j_jar, dir_path), "JavaServer" ]
        self.process = subprocess.Popen(cmd,  close_fds=True) #shell=True,
        sys.stderr.write("Started java process with pid %f" % self.process.pid)
        
        # wait so that server starts
        time.sleep(2)
        
        # connect to the JVM
        self.gateway = JavaGateway()
        
        # get the application instance
        self.bpInstance = self.gateway.entry_point
        
        # call the method get_BP_obj() in java
        self.bp_obj = self.bpInstance.get_BP_obj(grammarfile)
    
    
    def parse(self, sentence_string):
        """
        It calls the parse function on BParser object.
        """
         
        # call the python function parse() on BParser object
        return self.bp_obj.parse(sentence_string)
        
    
    def close(self):
        """
        Java server is terminated from here.
        """
        self.gateway.shutdown()
        sys.stderr.write( "trying to close process %f" % self.process.pid)
        self.process.terminate()

        
    def __del__(self):
        """
        Destroy object when object unloaded or program exited
        """
        self.close()
        

bps = BerkeleyParserSocket("/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr", "/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar")
bps2 = BerkeleyParserSocket("/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr", "/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar")
print bps2.parse("This is a sentence")
print bps.parse("This is another sentence")




