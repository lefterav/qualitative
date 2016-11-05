from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import argparse
from mt.moses import ProcessedMosesWorker, MosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker
import logging as log

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
parser.add_argument('--worker', 
                    help="[ProcessedMoses|Moses|NeuralMonkey] worker that performs the translation, defaults to ProcessedMoses", 
                    default="ProcessedMoses")
parser.add_argument('--debug', help="Enable verbose output", action='store_true') 
args = parser.parse_args()

loglevel = log.INFO
if args.debug:
    print "Enable debug verbose mode"
    loglevel = log.DEBUG
log.basicConfig(level=loglevel,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

worker_class = eval(args.worker+"Worker")
log.info("Loading server for {} on port {}".format(args.worker, args.port))
translator = worker_class(uri=args.uri, 
                          source_language=args.source_language,
                          target_language=args.target_language,
                          truecaser_model=args.truecaser_model,
                          splitter_model=args.splitter_model)

log.debug("Translator class: {}".format(translator))
server = SimpleXMLRPCServer((args.host, args.port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


def process_task(params):
    text = params['text']
    log.info("Received task\n")
    translated_text, description = translator.translate(text)
    log.debug(translated_text)
    transaction_id = 0
    result = {
            "errorCode": 0, 
            "errorMessage": "OK",
            "translation": [
                {
                    "translated": [
                        {
                            "text": translated_text, 
                            #"description": description,
                            "score": 0,
                        }
                    ], 
                }
            ], 
            "translationId": transaction_id
        }
    return result


server.register_function(process_task, 'process_task')
log.info("server {} ready on port {}".format(args.worker, args.port))
server.serve_forever()
