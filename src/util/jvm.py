'''
Created on 22 Jun 2012

@author: Eleftherios Avramidis
'''
import subprocess
import time
import os
from py4j.java_gateway import JavaGateway, GatewayClient, CallbackServerParameters, GatewayParameters
import logging as log
from py4j.tests.java_callback_test import IHelloImpl


def get_libs():
    """
    Return libs directory and files that need to be included in the java classpath
    @return: file patter and directories to be included in the java classpath
    @rtype: list(str)
    """
    path = os.path.abspath(__file__)
    components = path.split(os.sep)
    rootpath = os.path.join(os.sep, *components[:-3])
    libpath = os.path.join(rootpath, "lib")
    libpath_all = os.path.join(libpath, "*")   
    #get all subdirs
    dirs = [os.path.join(libpath, name) for name in os.listdir(libpath) if os.path.isdir(os.path.join(libpath, name)) ]
    dirs.extend([os.path.join(libpath, name, "*") for name in os.listdir(libpath) if os.path.isdir(os.path.join(libpath, name)) ])
    dirs.extend([libpath, libpath_all])
    return dirs


class LocalJavaGateway(JavaGateway):
    '''
    A single class that encapsulates a local Java Virtual Machine (JVM), and gets initialized
    as a local java gateway, connected to the socket of the JVM. The class extends
    the JavaGateway class of Py4j
    @var jvm: The local JVM process
    @var gatewayclient: The gateway client connected to the local socket of the JVM  
    '''
    def __init__(self, java="java"):
        self.jvm_process = JVM(java=java)
        log.info("Loaded JVM")
        socket_no = self.jvm_process.socket_no
        
        log.info("Loading Gateway Client on socket {}".format(socket_no))                
        self.gatewayclient = GatewayClient('localhost', socket_no)
        log.info("Launched Gateway on socket {}".format(socket_no))
                
        super(LocalJavaGateway, self).__init__(self.gatewayclient,
                                               callback_server_parameters=CallbackServerParameters(port=0), 
                                               auto_convert=True, 
                                               auto_field=True)
        
        # retrieve the port on which the python callback server was bound to.

        # tell the Java side to connect to the python callback server with the new
        # python port. Note that we use the java_gateway_server attribute that
        # retrieves the GatewayServer instance.
        log.info("Loaded Gateway")
    
    def shutdown(self):
        try:
            super(LocalJavaGateway, self).shutdown()
            log.info("Gateway was shut down properly")
        except:
            log.info("Gateway need not be shut down")
        try:
            self.jvm_object.terminate()
            log.info("JVM object terminated properly")
        except:
            log.info("JVM object need bot be terminated")
        pass
        
    def __del__(self):
        self.shutdown()
        super(LocalJavaGateway, self).__del__()
        

class JVM(object):
    '''
    A wrapper for the Py4J server of Java Virtual Machine, so that java libraries can be accessed via Py4J. 
    @ivar jvm: The object of the wrapped Java Virtual Machine process
    @ivar socket_no: The socket that the Java Server is responding to Py4J requests 
    @ivar pid: The system process id of the Java Server 
    '''

    def __init__(self, java_classpath='', java="java"):
        '''
        Start running java
        '''
           
        #java_classpath.extend(get_libs())
        default_java_classpath = get_libs()
        path = os.path.abspath(__file__)
        #java_classpath.append(os.path.dirname(path))
        
        classpath = ":".join(default_java_classpath)
        #classpath = ":".join([classpath, java_classpath])
        log.info("classpath = {}".format(classpath))

        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        #commenting out as it is better handled by bash script in /lib
        #try:
        #    subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % os.path.dirname(path) ])
        #except:
        #    pass
        
        # prepare and run Java server
        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
        cmd = [java, "-cp", classpath, "JavaServer" ]
        cmd = " ".join(cmd)
        log.info("Command: {}".format(cmd))
        
        self.jvm = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE) #shell=True,
        time.sleep(3)
        self.jvm.stdout.flush()
        response = self.jvm.stdout.readline().strip()
        log.info("response = {}".format(response))
        self.socket_no = int(response)
        self.pid = self.jvm.pid
        log.info("pid = {}".format(self.pid))
        
    def terminate(self):
        """
        Stop the Java Server
        """
        try:
            self.jvm.terminate()
            log.info("JVM process terminated properly")
        except:
            log.info("JVM process need not be terminated")
        pass

    
    def __del__(self):
        """
        Stop the Java Server if the object stops existing
        """
        try:
            self.terminate()
            log.info("JVM process terminated properly")
        except:
            log.info("JVM process need not be terminated")
        pass
