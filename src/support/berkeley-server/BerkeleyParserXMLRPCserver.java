
/**
 * 
 * @author 
 */
//sudo apt-get install  libxmlrpc3-client-java
import org.apache.xmlrpc.*;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.XmlRpcServerConfigImpl;
import org.apache.xmlrpc.webserver.ServletWebServer;
import org.apache.xmlrpc.webserver.WebServer;
import org.apache.xmlrpc.webserver.XmlRpcServlet;

import edu.berkeley.nlp.PCFGLA.Grammar;


public class BerkeleyParserXMLRPCserver  {

	
    private static final int port =  8682;
    


	public static void main (String [] args) {
		
		try {
	          WebServer webServer = new WebServer(port);
	          
	          XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
	        
	          PropertyHandlerMapping phm = new PropertyHandlerMapping();
	         
	          phm.addHandler("myParser", myParser.class);
	          xmlRpcServer.setHandlerMapping(phm);
	        
	          XmlRpcServerConfigImpl serverConfig =
	              (XmlRpcServerConfigImpl) xmlRpcServer.getConfig();
	          serverConfig.setEnabledForExtensions(true);
	          serverConfig.setContentLengthOptional(false);

	          webServer.start();

		} catch (Exception exception) {
		     System.err.println("JavaServer: " + exception);
		}

	}



}