'''
Feature generator from Berkeley PCFG parser by wrapping Berkeley class 
Created on Sep 21, 2011

@author: Lukas Poustka
@author: Eleftherios Avramidis
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
import signal
from util.jvm import JVM


#def handler(self, signum):
#    sys.stderr.write("Parsing timeout\n")
#    raise Exception("parse_timeout")

class BerkeleyParserSocket():
    """
    A flexible wrapper for the Berkeley parser. It starts the Berkeley parser as an object
    which can be called as a Python object. It requires presence of external java libraries.
    The advantage of this class (e.g. vs XMLRPC) is that it can fully control starting and 
    stopping the parsing engine within Python code.  
    @ival grammarfile:
    @ivar parsername: 
    """
    
#    def __init__(self, grammarfile, classpath):
    def __init__(self, grammarfile, gateway):
        """
        fetches full parsing details from the Berkeley Engine and  calculates full features upon request
        @param grammarfile: Location of grammar file to be loaded
        @type grammarfile: string
        @param gateway: Initialize a java gateway
        @type gateway: Py4J java gateway object        
        """
        self.grammarfile = grammarfile
        self.gateway = gateway
        
        bparser_class = os.path.dirname(__file__)
        dir_socket = os.path.dirname(bparser_class)                
        dir_berkeley = os.path.dirname(dir_socket)
        dir_parser = os.path.dirname(dir_berkeley)
        ####MODIFIED FOR USE WITH COMMANDLINE THING CHECK IF RUFFUS VERSION FAILS
        dir_src = os.path.dirname(dir_parser)
#        dir_featuregenerator = os.path.dirname(dir_parser)
#        dir_src = os.path.dirname(dir_featuregenerator)
        dir_lib = os.path.join(dir_src, "support", "berkeleyserver", "lib")
        
        print "Berkeley directory:" ,dir_lib
        
        #self.classpath = []
        #self.classpath.append(dir_lib)
        #self.classpath.append(bparser_class)
        #print "final classpath " , self.classpath
#        print "initializing Berkeley client"
##        try:
#        # connect to the JVM
#        classpath, dir_path = classpath
#
        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        #subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % dir_path])
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

#        except:
#            self._reconnect(berkeley_parser_jar, py4j_jar)
        self.parsername = random.randint(1,10000)
        self._connect(gateway, grammarfile)
    
    
    
    def _connect(self, gateway, grammarfile):        
        module_view = gateway.new_jvm_view()      
        java_import(module_view, 'BParser')
        
        # get the application instance
        self.bp_obj =  module_view.BParser(grammarfile)
        sys.stderr.write("got BParser object\n")

    
#    def _reconnect(self, berkeley_parser_jar, py4j_jar):
#        #define running directory
#        path = os.path.abspath(__file__)
#        dir_path = os.path.dirname(path)
#
#        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
#        subprocess.check_call(["javac", "-classpath", "%s:%s:%s" % (berkeley_parser_jar, py4j_jar, dir_path), "%s/JavaServer.java" % dir_path])
#        
#        
#        # prepare and run Java server
#        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
#        cmd = ["java", "-cp", "%s:%s:%s" % (self.berkeley_parser_jar, py4j_jar, dir_path), "JavaServer" ]
#        self.process = subprocess.Popen(cmd,  close_fds=True) #shell=True,
#        sys.stderr.write("Started java process with pid %d\n" % self.process.pid)
#        
#        # wait so that server starts
#        time.sleep(2)
#        self.gateway = JavaGateway()
#        bpInstance = self.gateway.entry_point
#    
#        # call the method get_BP_obj() in java
#        self.bp_obj = bpInstance.get_BP_obj(self.grammarfile)

    def parse(self, sentence_string):
        """
        It calls the parse function on BParser object.
        """
         
        # call the python function parse() on BParser object
#        try:
        sys.stderr.write("<p process='{0}' string='{1}'>\n".format(self.parsername, sentence_string))
        
#        signal.signal(signal.SIGALRM, handler)
#        signal.alarm(20)
        parseresult = None        
        while not parseresult:
            try:
                parseresult = self.bp_obj.parse(sentence_string)
#            except:
#                sys.stderr.write("Connection failed. Retrying ...")
#                time.sleep(5)
         
#        except Exception, exc: 
#            sys.stderr.write("Exception: {0}\n".format(exc))
#            parseresult = {}
                
        
            except:
                self._connect(self.gateway, self.grammarfile)
                parseresult = self.bp_obj.parse(sentence_string)
                sys.stderr.write("{0} crashed, restarting object".format(self.parsername))
        sys.stderr.write("<\p process='{0}' string='{1}'>\n".format(self.parsername, sentence_string))

        return parseresult
    
    
    def parse_msg(self, sentence_string):
        return self.bp_obj.parse(sentence_string)
        
        
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
        

if __name__ == "__main__":
    java_classpath = ["/home/Eleftherios Avramidis/.local/share/py4j/py4j0.7.jar:/home/Eleftherios Avramidis/tools/qualitative/src/support/berkeleyserver/lib/BerkeleyParser.jar:/home/Eleftherios Avramidis/tools/qualitative/src/featuregenerator/parser/berkeley/socket"]
    dir_path = "/home/Eleftherios Avramidis/workspace/qualitative/src/util"
    jvm = JVM(java_classpath)
    socket_no = jvm.socket_no
    gatewayclient = GatewayClient('localhost', socket_no)
    gateway = JavaGateway(gatewayclient, auto_convert=True, auto_field=True)

    bps = BerkeleyParserSocket("/home/elav01/tools/berkeleyparser/grammars/eng_sm6.gr", gateway)
#bps2 = BerkeleyParserSocket("/home/Eleftherios Avramidis/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr", "/home/Eleftherios Avramidis/workspace/TaraXUscripts/src/support/berkeley-server/lib/BerkeleyParser.jar", "/usr/share/py4j/py4j0.7.jar")
#print bps2.parse("This is a sentence")
#bps2.close()
    print bps.parse("This is another sentence")
#bps.close()




