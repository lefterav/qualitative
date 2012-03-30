//package py4j.examples;

import py4j.GatewayServer;

/**
 * This Java Server allows calling java functions from within Python. 
 * Just compile and run with Java, adding your required java code in the classpath.
 * ie:		javac -classpath mytool.jar:. JavaServer.java
 * 			java -classpath mytool.jar:. JavaServer
 * 
 * Then, you can access java object in Python, via Py4j:
 * 			from py4j.java_gateway import JavaGateway
 *          from py4j.java_gateway import java_import
 * 			gateway = JavaGateway()
 * 			module_view = gateway.new_jvm_view()
 *          java_import(module_view,'package1.package2.*')
 * 			java_list = gateway.jvm.java.util.ArrayList()
 * 			myobject = module_view.MyObject();
 * 
 * Note you have to run this only once, while you can instantiate as many 
 * JavaGateway()s you want. Py4j will handle all request via multiple java threads
 *  
 * @author Eleftherios Avramidis
 */

public class JavaServer {
	
    public static void main(String[] args) {
    	
    	boolean serverCreated = false;
		int socket = 25333;
		
		//keep trying to connect with the next socket, until socket is free
		while (!serverCreated) {
			try{
				System.err.println("Trying to start Java server in socket " + Integer.toString(socket));
				server = new GatewayServer(app, socket);
				server.start();
				serverCreated = true;
			} catch (Exception e) {
				server.shutdown();
				socket++;
			}
		}
		
		public static void shutdown() {
			server.shutdown();
			System.err.println("Java server terminated!");
		}
		
		System.out.println(Integer.toString(socket));
    }

}
