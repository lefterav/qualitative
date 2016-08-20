from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from app.autoranking.application import Autoranking
from mt.hybrid import DummyTriangleTranslator
import sys
from app.hybrid.translate import SimpleTriangleTranslator

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

if len(sys.argv) < 5:
    sys.exit("Usage: python xmlrpcserver.py <host> <port> <classifier_file> <annotation.config.1> [annotation.config.2 ...]")

host = sys.argv[1]
port = int(sys.argv[2])
param_moses_url = sys.argv[3]
param_lucy_url = sys.argv[4] 
param_lcm_url = sys.argv[5]
param_source_language = sys.argv[6]
param_target_language = sys.argv[7]
classifier_filename = sys.argv[8] # "/share/taraxu/selection-mechanism/wmt13/sentenceranking/autoranking_wmt13_newfeatures1_de_en/class_nameranklangpairde-eninclude_references0.0ties0.0trainset_modeannotatedattattset_24classifierLogReg/classifier.clsf"
configfilenames = sys.argv[9:]

#[
#                       '/home/elav01/workspace/qualitative/src/app/autoranking/config/pipeline.cfg',
#                       '/home/Eleftherios Avramidis/workspace/qualitative/src/app/autoranking/config/pipeline.wmt13metric.blade6.de.de-en.cfg'
# ]

# Create 
hybridsystem = SimpleTriangleTranslator(moses_url=param_moses_url, 
                                 lucy_url=param_lucy_url,
                                 lcm_url=param_lcm_url,
                                 source_language=param_source_language,
                                 target_language=param_target_language,
                                 configfilenames=configfilenames,
                                 classifiername=classifier_filename
                                 )

server = SimpleXMLRPCServer((host, port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


def process_task(params):
    text = params['text']
#    try:
    sys.stderr.write("Received task\n")
    translated_text, description = hybridsystem.translate(text)
    transaction_id = 0
    result = {
            "errorCode": 0, 
            "errorMessage": "OK",
            "translation": [
                {
                    "translated": [
                        {
                            "text": translated_text, 
                            "description": description,
                            "score": 0,
                        }
                    ], 
                }
            ], 
            "translationId": transaction_id
        }
    return result
#    except:
#        result = """{
#            "errorCode": 1, 
#            "errorMessage": "ERROR"
#            }"""
#        return result

server.register_function(process_task, 'process_task')
print "server ready"
server.serve_forever()
