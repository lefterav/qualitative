from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8088),
                            requestHandler=RequestHandler)
server.register_introspection_functions()



# Register a function under a different name
def qualityRank(originaldoc, mosestranslation, lucytranslation, googletranslation, langsrc, langtgt):
    #result=[[1,2,3], "Coefficient log likelikelyhood 45.4% dedscending azimuth by 290 degrees"]
    result="1$##$2$##$2$##$Coefficient log likelikelyhood 45.4% dedscending azimuth by 290 degrees"
    return result


def rank(originaldoc, mosestranslation, lucytranslation, googletranslation, langsrc, langtgt):
    result=[[3,2,1], "Logistic regression: Y=X^b+a where b=[parse=0.23, lm=0.14...] \n Moses X=[parse=0.13, lm=0.01...] \n Lucy X=[parse=0.11, lm=0.34...] \n\n Moses > Lucy \n Lucy < Google]"]
    return result
    
server.register_function(rank, 'rank')
server.register_function(qualityRank, 'qualityRank')

server.serve_forever()
