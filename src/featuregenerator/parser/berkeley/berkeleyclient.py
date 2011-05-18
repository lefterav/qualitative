import xmlrpclib 
import time
import sys
from featuregenerator.featuregenerator import FeatureGenerator
import socket


class BerkeleyFeatureGenerator(FeatureGenerator):
    '''
    classdocs
    '''


    def __init__(self, url, lang=""):
        '''
        Constructor
        '''
        self.server = xmlrpclib.Server(url)
        self.url = url
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
    
    #Warning: not language-aware function. Use the ones above
    def get_features_sentence(self, simplesentence, parallelsentence):
        sent_string = simplesentence.get_string()
        try:
            results = self.server.BParser.parse ( sent_string )
        except Exception as inst:
            print type(inst) 
            print inst
            return {}

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
    
    
    def add_features_batch(self, parallelsentences):
        batch = []
        preprocessed_batch = []
        for parallelsentence in parallelsentences:
            batch.append((parallelsentence.serialize(), parallelsentence.get_attribute("langsrc"),  parallelsentence.get_attribute("langtgt")))
        
        for (row, langsrc, langtgt) in batch:
            preprocessed_row = []
            col_id = 0
            for simplesentence in row:
                if (col_id == 0 and langsrc == self.lang) or (col_id > 0 and langtgt == self.lang):
                    simplesentence = simplesentence.get_string()
                    #simplesentence = self.__prepare_sentence_b64__(simplesentence)
                    preprocessed_row.append(simplesentence)
                else:
                    simplesentence = ""
                    preprocessed_row.append(simplesentence)
                col_id += 1
            preprocessed_batch.append(preprocessed_row)
        
        socket.setdefaulttimeout(None) 
        connected = False
        while not connected:
            #try:
            features_batch = self.server.BParser.parse_batch(preprocessed_batch)
            connected = True
            #except TimeoutException: TODO: find a better way to handle timeouts
            #    sys.stderr.write("Connection to server %s failed, trying again after a few seconds...\n" % self.url)
            #    time.sleep(5)
        
        row_id = 0

        
        new_parallelsentences = []
        for row in features_batch:
            parallelsentence = parallelsentences[row_id]
            src = parallelsentence.get_source()
            targets = parallelsentence.get_translations()
            
            column_id = 0
            #dig in the batch to retrieve features
            for feature_set in row:
                for key in feature_set:
                    if column_id == 0:
                        src.add_attribute(key, feature_set[key])
                    else:
                        targets[column_id - 1].add_attribute(key, feature_set[key])
                
                    
                column_id += 1
            
            parallelsentence.set_source(src)
            parallelsentence.set_translations(targets)
            new_parallelsentences.append(parallelsentence)
            row_id += 1
        
        return new_parallelsentences

    
    
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
        
    
