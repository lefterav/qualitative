

import py4j.GatewayServer;

public class JavaServer {
	
	
	static JavaServer app = new JavaServer();
	// app is now the gateway.entry_point
	static GatewayServer server;

	public static BParser get_BP_obj(String grammarfile) {
		System.err.println("Creating a BParser object...");
		BParser bp = new BParser(grammarfile);
		return bp;
	}
	
	public static void shutdown() {
		server.shutdown();
		System.err.println("Java server terminated!");
	}
	
	public static void main(String[] args) {
		boolean serverCreated = false;
		int socket = 25333;
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
		
		System.err.println("Java server started in socket " + Integer.toString(socket));
	}
}
