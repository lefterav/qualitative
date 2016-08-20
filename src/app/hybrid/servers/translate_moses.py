'''
Created on Aug 18, 2016

@author: lefterav
'''
from mt.moses import ProcessedWorker
from mt.neuralmonkey import NeuralMonkeyWorker

uri="http://blade-1.dfki.uni-sb.de:9502"
source_language="de"
target_language="en"
truecaser_model="/home/lefterav/workspace/qualitative/res/truecasers/truecase-model.3.de"
splitter_model="/home/lefterav/workspace/qualitative/res/splitter/split-model.de"

if __name__ == '__main__':
    translator = NeuralMonkeyWorker(uri,
                                      source_language,
                                      target_language,
                                      truecaser_model,
                                      splitter_model
                                      )
    print translator.translate("Ein Unternehmensverkehr, muss untersucht werden.")