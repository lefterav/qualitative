import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
 
class BerkeleyFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, url, lang=""):
        '''
        Constructor
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
    
    #TODO: see if scope of self.lang allows to move these 2 methods in featuregenerator class  
    def add_features_src(self, simplesentence, parallelsentence):
        src_lang = parallelsentence.get_attribute("langsrc")
        if src_lang == self.lang:
            atts = self.get_features_sentence(simplesentence, parallelsentence)
            simplesentence.add_attributes(atts)
        return simplesentence

    def add_features_tgt(self, simplesentence, parallelsentence):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            atts = self.get_features_sentence(simplesentence, parallelsentence)
            simplesentence.add_attributes(atts)
        return simplesentence      
        
    def get_features_sentence(self, simplesentence, parallelsentence):
        sent_string = simplesentence.get_string()
        results = self.server.BParser.parse ( sent_string )

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
        if n !=0:
            avg_confidence = sum_confidence / n
        else:
            avg_confidence = -float('inf')
        
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
        
    
