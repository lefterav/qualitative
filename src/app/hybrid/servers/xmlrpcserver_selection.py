from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import argparse
from mt.moses import ProcessedMosesWorker, MosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker

from app.hybrid.translate_selection import parse_args, set_loglevel
from mt.hybrid import Pilot3Translator
 

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    
args = parse_args()


server = SimpleXMLRPCServer((args.host, args.port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

args = parse_args()
set_loglevel(args.debug)
translator = Pilot3Translator(args.engines, args.config, 
                                  args.source_language, 
                                  args.target_language, 
                                  args.ranking_model,
                                  args.reverse)


def process_task(params):
    text = params['text']
    sys.stderr.write("Received task\n")
    translated_text, description = translator.translate(text)
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


server.register_function(process_task, 'process_task')
print "server ready"
server.serve_forever()
