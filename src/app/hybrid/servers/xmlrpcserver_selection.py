from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import argparse
from mt.moses import ProcessedMosesWorker, MosesWorker
from mt.neuralmonkey import NeuralMonkeyWorker

from app.hybrid.translate_selection import set_loglevel
from mt.hybrid import Pilot3Translator

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',) 

def parse_args():

    parser = argparse.ArgumentParser(description="Run translate engines and selection mechanism on a file")
    parser.add_argument('--engines', nargs='*', default=['Lucy', 'Moses', 'NeuralMonkey'],
                        help="A list of the names of the engines for translating, in the prefered order")
    parser.add_argument('--translated_textfiles', '-t', nargs='*', default=None,
                        help="If translations have been performed, they can be given here in simple text files \
                        so that only selection takes place. The text filenames should be provided \
                        in respective order to the list of engine names passed by --engines. If this argument is \
                        not given, the translations will be fetched from the given engines")
    parser.add_argument('--source_language', default='en', help="The language code of the source language")
    parser.add_argument('--target_language', default='de', help="The language code of the target language")
    parser.add_argument('--config', nargs='*', 
                        help="A list of configuration files for the engines and the feature generators")
    parser.add_argument('--ranking_model',
                        help="The path of the file containing a ranker, as a result of the training process")
    parser.add_argument('--input', help="The location of a text file to be translated")
    parser.add_argument('--host', help="The name of the host")
    parser.add_argument('--port', help="The port that the server will be responding to")
    parser.add_argument('--debug', action='store_true', default=False, help="Run in full verbose mode")   
    parser.add_argument('--reverse', action='store_true', default=False,
                        help="Whether ranker's decisions should be reversed. Useful if ranker trained with BLEU or meteor \
                        and not reversed before it was stored.")
    args = parser.parse_args()
    return args

   
args = parse_args()


server = SimpleXMLRPCServer((args.host, int(args.port)),
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
    translated_text, _, description = translator.translate(text)
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
print "server ready"
server.serve_forever()
