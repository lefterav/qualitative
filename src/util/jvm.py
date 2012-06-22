'''
Created on 22 Jun 2012

@author: elav01
'''
import subprocess
import time

class JVM(object):
    '''
    classdocs
    '''


    def __init__(self, java_classpath, dir_path):
        '''
        Constructor
        '''
        classpath  = ":".join(java_classpath) 
        
        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        #subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % dir_path])
            
        print "classpath = ", classpath
         
        #since code ships without compiled java, we run this command to make sure that the necessary java .class file is ready
        subprocess.check_call(["javac", "-classpath", classpath, "%s/JavaServer.java" % dir_path ])
        
        # prepare and run Java server
        #cmd = "java -cp %s:%s:%s JavaServer" % (berkeley_parser_jar, py4j_jar, dir_path)        
        cmd = ["java", "-cp", classpath, "JavaServer" ]
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