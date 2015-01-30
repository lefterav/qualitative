'''
Created on 22 Jun 2012

@author: Eleftherios Avramidis
'''
import subprocess
import time
import os

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
    dirs = [os.path.join(libpath, name, "*") for name in os.listdir(libpath) if os.path.isdir(os.path.join(libpath, name)) ]
    dirs.extend([libpath, libpath_all])
    return dirs

class JVM(object):
    '''
    A wrapper for the Py4J server of Java Virtual Machine, so that java libraries can be accessed via Py4J. 
    @ivar jvm: The object of the wrapped Java Virtual Machine process
    @ivar socket_no: The socket that the Java Server is responding to Py4J requests 
    @ivar pid: The system process id of the Java Server 
    '''

    def __init__(self, java_classpath):
        '''
        Star running java
        '''
           
        #java_classpath.extend(get_libs())
        default_java_classpath = get_libs()
        path = os.path.abspath(__file__)
        #java_classpath.append(os.path.dirname(path))
        
        classpath = ":".join(default_java_classpath)
        classpath = ":".join([classpath, java_classpath])
        print "classpath = ", classpath

        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        #commenting out as it is better handled by bash script in /lib
        #try:
        #    subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % os.path.dirname(path) ])
        #except:
        #    pass
        
        # prepare and run Java server
        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
        cmd = ["java", "-cp", classpath, "JavaServer" ]
        print cmd
        cmd = " ".join(cmd)
        
        self.jvm = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE) #shell=True,
        time.sleep(3)
        self.jvm.stdout.flush()
        self.socket_no = int(self.jvm.stdout.readline().strip())
        self.pid = self.jvm.pid
        
    def terminate(self):
        """
        Stop the Java Server
        """
        self.jvm.terminate()
    
    
    def __del__(self):
        """
        Stop the Java Server if the object stops existing
        """
        try:
            self.jvm.terminate()
        except:
            pass
