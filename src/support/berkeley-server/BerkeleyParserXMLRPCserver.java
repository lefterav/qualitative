
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

import edu.berkeley.nlp.PCFGLA.CoarseToFineMaxRuleParser;


public class BerkeleyParserXMLRPCserver  {

	
    //private static final int port =  8682;
    


	public static void main (String [] args) {
		
		if (args.length < 1){
			System.err.print("Please provide one argument with the port number");
		}
		
		Integer port = Integer.valueOf(args[0]);
		String grammarFile = args[1];
		
		try {
	          WebServer webServer = new WebServer(port);
	          
	          XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
	        
	          PropertyHandlerMapping phm = new PropertyHandlerMapping();
	          
	          //bParser bparser = new bParser( "/home/elav01/taraxu_tools/berkeleyParser/grammars/eng_sm6.gr" );
	         
	          //phm.addHandler("bParser", bparser.getClass());
	          
	          phm.setRequestProcessorFactoryFactory(new BParserRequestProcessorFactoryFactory( grammarFile ));
	          phm.setVoidMethodEnabled(true);
	          phm.addHandler(BParser.class.getName(), BParser.class);
	          
	          xmlRpcServer.setHandlerMapping(phm);
	          
	        
	          XmlRpcServerConfigImpl serverConfig =
	              (XmlRpcServerConfigImpl) xmlRpcServer.getConfig();
	          serverConfig.setEnabledForExtensions(true);
	          serverConfig.setContentLengthOptional(false);

	          webServer.start();

		} catch (Exception exception) {

			exception.printStackTrace();
		}

	}



}