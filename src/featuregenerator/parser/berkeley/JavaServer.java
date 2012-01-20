

import py4j.GatewayServer;

public class JavaServer {
	
	
	static JavaServer app = new JavaServer();
	// app is now the gateway.entry_point
	static GatewayServer server = new GatewayServer(app, 25333);

	public static BParser get_BP_obj(String grammarfile) {
		System.out.println("Creating a BParser object...");
		BParser bp = new BParser(grammarfile);
		return bp;
	}
	
	public void shutdown_server() {
		server.shutdown();
		System.out.println("Java server terminated!");
	}
	
	public static void main(String[] args) {
		server.start();
		System.out.println("Java server started!");
	}
}
