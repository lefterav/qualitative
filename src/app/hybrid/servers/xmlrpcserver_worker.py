from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from app.autoranking.application import Autoranking
import sys
import argparse
from mt.moses import ProcessedMosesWorker, MosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    
parser = argparse.ArgumentParser(description='XML RPC server front for pre- and post-processing Moses SMT')
parser.add_argument('--host', help="Host name where XML RPC server will run")
parser.add_argument('--port', type=int, help="Port where XML RPC server will respond")
parser.add_argument('--uri', help="URI where Moses server responds")
parser.add_argument('--source_language', help="source language 2-letter code")
parser.add_argument('--target_language', help="target language 2-letter code")
parser.add_argument('--truecaser_model', help="filename of the truecasing model")
parser.add_argument('--splitter_model', default=None, help="filename of the compound splitting model")
parser.add_argument('--worker', default="ProcessedMoses")
args = parser.parse_args()

worker_class = eval(args.worker+"Worker")
translator = worker_class(uri=args.uri, 
                          source_language=args.source_language,
                          target_language=args.target_language,
                          truecaser_model=args.truecaser_model,
                          splitter_model=args.splitter_model)
server = SimpleXMLRPCServer((args.host, args.port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


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
