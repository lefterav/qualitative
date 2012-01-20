'''
Created on Sep 21, 2011

@author: jogin
'''

from py4j.java_gateway import JavaGateway #@UnresolvedImport
from subprocess import Popen
import time


class BerkeleyParserSocket():
    """
    This class enables running java methods for BParser.java from Python.
    """
    def __init__(self, berkeley_parser_jar, py4j_jar, java_server_loc):
        """
        @param berkeley_parser_jar: Location of BerkeleyParser.jar
        @type berkeley_parser_jar: string
        @param py4j_jar: Location of py4j.jar
        @type py4j_jar: string
        @param java_server_loc: Location of JavaServer.class
        @type java_server_loc: string
        
        Example use
        
        bps = BerkeleyParserSocket("/home/elav01/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar", "/home/elav01/workspace/TaraXUscripts/src/featuregenerator/parser/berkeley/", "/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr")
        print bps.parse("This is a sentence")
        # if the server wasn't closed, it has to be done manually in cmdline ('kill <PID>')
        # with local address 25333 specified in JavaServer.java 
        bps.shutdown_server()
        
        """
        cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, java_server_loc)
        
        # run Java server
        Popen(cmd, shell=True, close_fds=True)
        
        # wait till server starts
        time.sleep(1)
        
        # connect to the JVM
        self.gateway = JavaGateway()
        
        # get the AdditionApplication instance
        self.bpInstance = self.gateway.entry_point
        
        # call the method get_BP_obj() in java
        self.bp_obj = self.bpInstance.get_BP_obj()
    
    
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



