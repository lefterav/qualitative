'''
Created on Aug 18, 2016

@author: lefterav
'''
from mt.moses import ProcessedMosesWorker

uri="http://lns-87247.dfki.uni-sb.de:9202"
source_language="en"
target_language="de"
truecaser_model="/home/lefterav/workspace/qualitative/res/truecasers/truecase-model.3.en"

if __name__ == '__main__':
    translator = ProcessedMosesWorker(uri,
                                      source_language,
                                      target_language,
                                      truecaser_model
                                      )
    print translator.translate("This is a test")