import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcRequest;
import org.apache.xmlrpc.server.RequestProcessorFactoryFactory;
import org.apache.xmlrpc.server.RequestProcessorFactoryFactory.StatelessProcessorFactoryFactory;


public class BParserRequestProcessorFactoryFactory implements RequestProcessorFactoryFactory {
	
	private final RequestProcessorFactory factory = new BParserRequestProcessorFactory();

	private final BParser bparser; 

	/**
	 * Initializes the parser once given the specific grammar file
	 * @param inFileName parser grammar file
	 */
	public BParserRequestProcessorFactoryFactory(  String inFileName  ){
		this.bparser = new BParser(inFileName);
	}
	
	
	@Override
	public RequestProcessorFactory getRequestProcessorFactory(Class arg0)
			throws XmlRpcException {
		return factory;
	}
	
	/**
	 * 
	 * 
	 */
	private class BParserRequestProcessorFactory implements RequestProcessorFactory {

		@Override
		/**
		 * Provides the initialized bparser class as a request processor
		 */
		public Object getRequestProcessor(XmlRpcRequest xmlRpcRequest)
				throws XmlRpcException {

			return bparser;
		}
	}

	
	


}
