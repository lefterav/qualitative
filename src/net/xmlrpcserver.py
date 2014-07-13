from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from app.autoranking.application import Autoranking

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create ranker
classifier_filename = "/share/taraxu/selection-mechanism/wmt13/sentenceranking/autoranking_wmt13_newfeatures1_de_en/class_nameranklangpairde-eninclude_references0.0ties0.0trainset_modeannotatedattattset_24classifierLogReg/classifier.clsf"
configfilenames = [
                       '/home/elav01/workspace/qualitative/src/app/autoranking/config/pipeline.cfg',
                       '/home/elav01/workspace/qualitative/src/app/autoranking/config/pipeline.wmt13metric.blade6.de.de-en.cfg'
                       ]

# Create 
autoranker = Autoranking(configfilenames, classifier_filename)
server = SimpleXMLRPCServer(("lns-87004.sb.dfki.de", 8089),
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
