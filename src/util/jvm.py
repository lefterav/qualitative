'''
Created on 22 Jun 2012

@author: Eleftherios Avramidis
'''
import subprocess
import time
import os
import fnmatch


def get_libs():
    path = os.path.abspath(__file__)
    components = path.split(os.sep)
    rootpath = os.path.join(os.sep, *components[:-3])
    libpath = os.path.join(rootpath, "lib")    
    libs = [os.path.join(libpath, f) for f in os.listdir(libpath) if f.endswith('.jar') or f.endswith('.class')]
    libs.append(libpath)
    return libs
    


class JVM(object):
    '''
    classdocs
    '''

    def __init__(self, java_classpath):
        '''
        Constructor
        '''
        
        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        #subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % dir_path])
            
        #java_classpath.extend(get_libs())
        java_classpath = get_libs()
        path = os.path.abspath(__file__)
        libdir = path
        java_classpath.append(os.path.dirname(path))
        
        classpath = ":".join(java_classpath)
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
#            cmd = " ".join(cmd)
        
        self.jvm = subprocess.Popen(cmd, shell=False, bufsize=0, stdout=subprocess.PIPE) #shell=True,
        time.sleep(10)
        self.jvm.stdout.flush()
        self.socket_no = int(self.jvm.stdout.readline().strip())
        self.pid = self.jvm.pid
        
    def terminate(self):
        self.jvm.terminate()
    
    
    def __del__(self):
        try:
            self.jvm.terminate()
        except:
            pass
