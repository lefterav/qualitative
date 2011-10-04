'''
Created on Sep 21, 2011

@author: jogin
'''

from py4j.java_gateway import JavaGateway
from subprocess import Popen
import time


class BerkeleyParserSocket():
    """
    This class enables running java methods for BParser.java from Python.
    """
    def __init__(self, berkeley_parser_loc, py4j_loc, java_server_loc):
        """
        @param berkeley_parser_loc: Location of BerkeleyParser.jar
        @type berkeley_parser_loc: string
        @param py4j_loc: Location of py4j.jar
        @type py4j_loc: string
        @param java_server_loc: Location of JavaServer.class
        @type java_server_loc: string
        """
        cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_loc, py4j_loc, java_server_loc)
        
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
    
    
    def parse(self):
        """
        It calls the parse function on BParser object.
        """
        line = "this is a sentence to parse"
        # call the python function parse() on BParser object
        self.bp_obj.parse(line)
        
    
    def shutdown_server(self):
        """
        Java server is terminated from here.
        """
        self.gateway.shutdown()
