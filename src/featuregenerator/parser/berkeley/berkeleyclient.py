import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 
class BerkeleyFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, url):
        '''
        Constructor
        '''
        self.s = xmlrpclib.Server(url)
        
    def get_features_sentence(self, simplesentence, parallelsentence):
        sent_string = simplesentence.get_string()
        results = self.s.bParser.parse ( sent_string )

        loglikelihood = results['loglikelihood']
        nbestList = results['nbest']
        n = len(nbestList)

        best_confidence = -1e308;
        best_parse = ""
        sum_confidence = 0
        
        print "analyzing tree statistics",
        for entry in nbestList:
            confidence = entry["confidence"]
            parse = entry["tree"]
            if float(confidence) > best_confidence:
                best_confidence = float(confidence)
                best_parse = parse
            sum_confidence += float(confidence)
        
        print
        avg_confidence = sum_confidence / n
        
        attributes={}
        attributes ["berkeley-n"] = str(n)
        attributes ["berkley-loglikelihood"] = str(results['loglikelihood'])
        attributes ["berkeley-best-parse-confidence"] = str(best_confidence)
        attributes ["berkeley-avg-confidence"] = str(avg_confidence)
        attributes ["berkeley-tree"] = best_parse
        return attributes
    
    
    def parse(self, string):

        results = self.s.bParser.parse ( string )
        loglikelihood = results['loglikelihood']
        nbestList = results['nbest']
        n = len(nbestList)
        

        
        best_confidence = -1e308;
        best_parse = ""
        sum_confidence = 0
        
        for entry in nbestList:
            confidence = entry["confidence"]
            parse = entry["tree"]
            if float(confidence) > best_confidence:
                best_confidence = float(confidence)
                best_parse = parse
            sum_confidence += float(confidence)
            
        avg_confidence = sum_confidence / n
        
        print "berkeley-n" + str(n)
        print "berkley-loglikelihood" + str(results['loglikelihood'])
        print "berkeley-best-parse-confidence" , best_confidence
        print "berkeley-avg-confidence" , avg_confidence
        print "berkeley-best-parse-tree" , best_parse
        
    
