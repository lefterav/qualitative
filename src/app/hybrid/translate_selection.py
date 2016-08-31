'''
Created on Aug 19, 2016

@author: lefterav
'''


from mt.moses import ProcessedWorker
from mt.neuralmonkey import NeuralMonkeyWorker
from mt.hybrid import Pilot3Translator
import argparse
import logging as log
import sys

#uri="http://blade-1.dfki.uni-sb.de:9502"
source_language="de"
target_language="en"
truecaser_model="/home/lefterav/workspace/qualitative/res/truecasers/truecase-model.3.de"
splitter_model="/home/lefterav/workspace/qualitative/res/splitter/split-model.de"


parser = argparse.ArgumentParser(description="Run translate engine on a file")
parser.add_argument('--engines', nargs='*', action='append', default=['Moses','Lucy','LcM'])
parser.add_argument('--source_language', default='en')
parser.add_argument('--target_language', default='de')
parser.add_argument('--config', nargs='*', default=["/home/lefterav/workspace/qualitative/config/autoranking/features.dev.cfg",
                                              "/home/lefterav/workspace/qualitative/config/autoranking/mt.cfg"
                                              ])
parser.add_argument('--ranking_model', default="/home/lefterav/workspace/qualitative/res/qe/0.model.dump")
parser.add_argument('--debug', type=bool, default=False)
args = parser.parse_args()

if __name__ == '__main__':
    loglevel = log.INFO
    if "--debug" in sys.argv:
        loglevel = log.DEBUG
    log.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')  
    log.debug("Read config filenames from commandline {}".format(args.config))
    translator = Pilot3Translator(args.engines, args.config, 
                                  args.source_language, 
                                  args.target_language, 
                                  args.ranking_model)
    print translator.translate("Ein Unternehmensverkehr muss untersucht werden")
