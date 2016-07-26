from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from app.autoranking.application import Autoranking
import sys

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

if len(sys.argv) < 5:
    sys.exit("Usage: python xmlrpcserver.py <host> <port> <classifier_file> <annotation.config.1> [annotation.config.2 ...]")

host = sys.argv[1] #e.g. lns-87004.sb.dfki.de",
port = int(sys.argv[2]) # eg. 8089
classifier_filename = sys.argv[3] # "/share/taraxu/selection-mechanism/wmt13/sentenceranking/autoranking_wmt13_newfeatures1_de_en/class_nameranklangpairde-eninclude_references0.0ties0.0trainset_modeannotatedattattset_24classifierLogReg/classifier.clsf"
configfilenames = sys.argv[4:]

#[
#                       '/home/elav01/workspace/qualitative/src/app/autoranking/config/pipeline.cfg',
#                       '/home/Eleftherios Avramidis/workspace/qualitative/src/app/autoranking/config/pipeline.wmt13metric.blade6.de.de-en.cfg'
                      # ]

# Create 
autoranker = Autoranking(configfilenames, classifier_filename)
server = SimpleXMLRPCServer((host, port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()



# Register a function under a different name
def rank(source, mosestranslation, lucytranslation, googletranslation, langsrc, langtgt):

    
    output = autoranker.rank(source, [mosestranslation, lucytranslation, googletranslation])
    result= str(output)

    return result


def qualityRank(source, mosestranslation, lucytranslation, googletranslation, langsrc, langtgt):

    ranking, description = autoranker.rank(source, [mosestranslation, lucytranslation, googletranslation])
    result="{rank1}$##${rank2}$##${rank3}$##${description}".format(rank1=ranking[0],
                                                                   rank2=ranking[1],
                                                                   rank3=ranking[2],
                                                                   description=description)
    return result
    


    
server.register_function(rank, 'rank')
server.register_function(qualityRank, 'qualityRank')
print "server ready"
server.serve_forever()
