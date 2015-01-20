import xmlrpclib



class Worker:
    """
    Abstract class for translation engine workers
    """
    def translate(self, string):
        """
	Translate given string and return the result and any translation information
	@param string: the string to be translated
	@type string: string
	@return translated_string, translation_info
	@rtype: string, dict of (string, float) or (string, int) or (string, string)
	"""
	raise NotImplementedError("This function needs to be implemented by a subclass of Worker")


class MosesWorker:
    """
    Wrapper class for Moses server
    """
    def __init__(self, uri, **params):
        """
	Initialize connection to Moses server
	@param uri: ip address or url of mosesserver followed by : and the port number
	@type uri: string
	"""
        #initialize XML rpc client
	#throw error if Moses server not started
        #self.server = xmlrpc.initialize("{}:{}".format(address, port))
	self.server = xmlrpclib.ServerProxy(uri)

    def translate(self, string):
        #send request to moses client
        #response = self.server.translate(string)


class LucyWorker:
    """
    """
    def 

class HybridTranslator:
    def __init__(self, workers):
        self.workers = workers
        pass
    
    def process(self, source_string):
        translated_string = None
        #TODO
        return translated_string 



if __name__ == '__main__':
    run()

