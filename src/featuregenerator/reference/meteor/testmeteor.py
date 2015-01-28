'''
Testing function for METEOR classes
Created on 22 Jun 2012

@author: Eleftherios Avramidis
'''
from py4j.java_gateway import JavaGateway, GatewayClient, java_import

import multiprocessing, time, random
from util.jvm import JVM

def singlethread(java_classpath):
    print "Thread starting"
    
    jvm = JVM(java_classpath, dir_path)
    socket_no = self.jvm.socket_no
    gatewayclient = GatewayClient('localhost', socket_no)
    gateway = JavaGateway(gatewayclient, auto_convert=True, auto_field=True)
    sys.stderr.write("Initialized global Java gateway with pid {} in socket {}\n".format(self.jvm.pid, socket_no))

    
    gatewayclient = GatewayClient('localhost', socket_no)
    print "Gclient started"
    gateway = JavaGateway(gatewayclient, auto_convert=True, auto_field=True)
    print "Java Gateway started"
    #create a new view for the jvm
    meteor_view = gateway.new_jvm_view()
    #import required packages
    java_import(meteor_view, 'edu.cmu.meteor.scorer.*')
    #initialize the java object
    java_import(meteor_view, 'edu.cmu.meteor.util.*')
    print "Modules imported"
    #pass the language setting into the meteor configuration object
    config = meteor_view.MeteorConfiguration();
    config.setLanguage("en");
    scorer = meteor_view.MeteorScorer(config)
    print "object initialized"
    #run object function
    stats = scorer.getMeteorStats("Test sentence", "Test sentence !");
    print stats.score
    return 1


if __name__ == '__main__':
    
#    gatewayclient = GatewayClient('localhost', socket_no)

    java_classpath = ""

    p = multiprocessing.Pool(3)
    print "Multipool initialized"
    p.map(singlethread, [java_classpath, java_classpath, java_classpath])
    




if __name__ == '__main__':
    pass