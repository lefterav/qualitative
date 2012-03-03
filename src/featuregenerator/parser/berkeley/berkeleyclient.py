# -*- coding: utf-8 -*-
import xmlrpclib 
import time
import sys
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
import socket
from nltk import PunktWordTokenizer, PunktSentenceTokenizer
from featuregenerator.parser.berkeley.socket.berkeleyparsersocket import BerkeleyParserSocket


class BerkeleyFeatureGenerator(LanguageFeatureGenerator):

    def __init__(self, *args):
        raise NotImplementedError( "BerkeleyFeatureGenerator class has been deprecated. Please use either of the subclasses" )

    def parse(self, string):
        raise NotImplementedError( "BerkeleyFeatureGenerator class has been deprecated. Please use either of the subclasses" )
    
    def add_features_batch(self, parallelsentences):
        raise NotImplementedError( "BerkeleyFeatureGenerator class has been deprecated. Please use either of the subclasses" )
    
    #Warning: not language-aware function. Use the ones above
    def get_features_simplesentence(self, simplesentence, parallelsentence):
        sent_string = self.prepare_sentence(simplesentence)
        return self.get_features_string(sent_string)
        
    def get_features_string(self, sent_string):
        results = self.parse(sent_string)
        loglikelihood = results['loglikelihood']
        nbestList = results['nbest']
        n = len(nbestList)

        best_confidence = -1e308;
        best_parse = ""
        sum_confidence = 0
        
        #print "analyzing tree statistics",
        for entry in nbestList:
            confidence = entry["confidence"]
            parse = entry["tree"]
            if float(confidence) > best_confidence:
                best_confidence = float(confidence)
                best_parse = parse
            sum_confidence += float(confidence)
        
        #print
        if n !=0:
            avg_confidence = sum_confidence / n
        else:
            avg_confidence = -float('inf')
        
        attributes = {}
        attributes ["berkeley-n"] = str(n)
        attributes ["berkley-loglikelihood"] = str(loglikelihood)
        attributes ["berkeley-best-parse-confidence"] = str(best_confidence)
        attributes ["berkeley-avg-confidence"] = str(avg_confidence)
        attributes ["berkeley-tree"] = best_parse
        return attributes
    
    def prepare_sentence(self, simplesentence):
        
        string =  simplesentence.get_string()
        if self.tokenize:   
            string = string.replace(u'“', u'"')
            strings = PunktSentenceTokenizer().tokenize(string)
            fixed_string = []
            for string in strings:
                tokens = PunktWordTokenizer().tokenize(string)
                tokens[-1] = tokens[-1].replace(".", " .")
                fixed_string.extend(tokens)
            string = " ".join(fixed_string) 
        return string
    

#        batch = []
#        preprocessed_batch = []
#        for parallelsentence in parallelsentences:
#            batch.append((parallelsentence.serialize(), parallelsentence.get_attribute("langsrc"),  parallelsentence.get_attribute("langtgt")))
#        
#        for (row, langsrc, langtgt) in batch:
#            preprocessed_row = []
#            col_id = 0
#            for simplesentence in row:
#                if (col_id == 0 and langsrc == self.lang) or (col_id > 0 and langtgt == self.lang):
#                    simplesentence = simplesentence.get_string()
#                    #simplesentence = self.__prepare_sentence_b64__(simplesentence)
#                    preprocessed_row.append(simplesentence)
#                else:
#                    simplesentence = ""
#                    preprocessed_row.append(simplesentence)
#                col_id += 1
#            preprocessed_batch.append(preprocessed_row)
#        
#        socket.setdefaulttimeout(None) 
#        connected = False
#        while not connected:
#            #try:
#            features_batch = self.server.BParser.parse_batch(preprocessed_batch)
#            connected = True
#            #except TimeoutException: TODO: find a better way to handle timeouts
#            #    sys.stderr.write("Connection to server %s failed, trying again after a few seconds...\n" % self.url)
#            #    time.sleep(5)
#        
#        row_id = 0
#
#        
#        new_parallelsentences = []
#        for row in features_batch:
#            parallelsentence = parallelsentences[row_id]
#            src = parallelsentence.get_source()
#            targets = parallelsentence.get_translations()
#            
#            column_id = 0
#            #dig in the batch to retrieve features
#            for feature_set in row:
#                for key in feature_set:
#                    if column_id == 0:
#                        src.add_attribute(key, feature_set[key])
#                    else:
#                        targets[column_id - 1].add_attribute(key, feature_set[key])
#                
#                    
#                column_id += 1
#            
#            parallelsentence.set_source(src)
#            parallelsentence.set_translations(targets)
#            new_parallelsentences.append(parallelsentence)
#            row_id += 1
#        
#        return new_parallelsentences


    
#    
#    def parse(self, string):
#
#        results = self.server.BParser.parse ( string )
#        loglikelihood = results['loglikelihood']
#        nbestList = results['nbest']
#        n = len(nbestList)
#        
#
#        
#        best_confidence = -1e308;
#        best_parse = ""
#        sum_confidence = 0
#        
#        for entry in nbestList:
#            confidence = entry["confidence"]
#            parse = entry["tree"]
#            if float(confidence) > best_confidence:
#                best_confidence = float(confidence)
#                best_parse = parse
#            sum_confidence += float(confidence)
#            
#        avg_confidence = sum_confidence / n
#        
#        print "berkeley-n" + str(n)
#        print "berkley-loglikelihood" + str(results['loglikelihood'])
#        print "berkeley-best-parse-confidence" , best_confidence
#        print "berkeley-avg-confidence" , avg_confidence
#        print "berkeley-best-parse-tree" , best_parse
        

class BerkeleySocketFeatureGenerator(BerkeleyFeatureGenerator):
    """
    Class that handles the feature generation functions by calling Berkeley parser 
    through a socket connection. This class has the advantage that it gets controlled
    fully by python code. So many parsers can be started and run in parallel, e.g. 
    for speeding up parsing process via parallelization. 
    This may be a problem when parser is too big and can only be loaded once for many
    experiments. In that case use an XMLRPC server    
    """
    
    def __init__(self, grammarfile, berkeley_parser_jar, py4j_jar, lang = "", tokenize = False):
        self.lang = lang
        self.tokenize = tokenize
        self.berkeleyparser = BerkeleyParserSocket(grammarfile, berkeley_parser_jar, py4j_jar)
    
    def parse(self, string):
        return self.berkeleyparser.parse(string)
    
#    def __del__(self):
#        try:
#            self.berkeleyparser.__del__()
#        except:
#            pass
    
        

class BerkeleyXMLRPCFeatureGenerator(BerkeleyFeatureGenerator):
    def __init__(self, url, lang="", tokenize = False):
        '''
        Handles the connection with a Berkeley Server through XML-RPC
        '''
        self.server = xmlrpclib.ServerProxy(url)
        self.url = url
        self.lang = lang
        self.tokenize = tokenize
    
    def parse(self, string):
        connected = False
        failed = 0
        while not connected:
            try:
                results = self.server.BParser.parse (string)
                connected = True
                
            except Exception as inst:
                print type(inst),  inst
                time.sleep(0.5)
                failed += 1
        return results    

    
    def add_features_batch(self, parallelsentences):
        row_id = 0

        if parallelsentences[0].get_attribute("langsrc") == self.lang:
            batch = [[self.prepare_sentence(parallelsentence.get_source())] for parallelsentence in parallelsentences]

            features_batch = self.xmlrpc_call(batch) #self.server.getNgramFeatures_batch(batch)
            
            
            for row in features_batch:
                parallelsentence = parallelsentences[row_id]
                src = parallelsentence.get_source()
                
                #dig in the batch to retrieve features
                
                for feature_set in row:
                    for key in feature_set:
                        src.add_attribute(key, feature_set[key])
                        #print "type" , feature_set[key], type(feature_set[key])
                        
                parallelsentence.set_source(src)
                #parallelsentence.set_translations(targets)
                parallelsentences[row_id] = parallelsentence
                row_id += 1
        elif  parallelsentences[0].get_attribute("langtgt") == self.lang:
            batch = [[self.prepare_sentence(translation) for translation in parallelsentence.get_translations()] for parallelsentence in parallelsentences]

            features_batch = self.xmlrpc_call_batch(batch) 
            
            for row in features_batch:
                parallelsentence = parallelsentences[row_id]
                targets = parallelsentence.get_translations()
                
                column_id = 0
                #dig in the batch to retrieve features
                for feature_set in row:
                    for key in feature_set:
                        targets[column_id].add_attribute(key, feature_set[key])
                                            
                    column_id += 1
                
                #parallelsentence.set_source(src)
                parallelsentence.set_translations(targets)
                parallelsentences[row_id] = parallelsentence
                row_id += 1
        return parallelsentences
    
    def xmlrpc_call_batch(self, batch):
        socket.setdefaulttimeout(None) 
        connected = False
        features_batch = []
        while not connected:
            try:
                features_batch = self.server.BParser.parse_batch(batch)
                connected = True
            except xmlrpclib.Fault, err:
                print "Fault code: %d" % err.faultCode
                print "Fault string: %s" % err.faultString
                print "\nconnection failed, sleeping for 5 sec"
                time.sleep(5)
            except socket.timeout:
                print "time out, doing something..."
                time.sleep(5)
            except Exception, errorcode:
                if errorcode[0] == 111:
                    print "error 10035, doing something..."
                    time.sleep(5)
            #except TimeoutException: TODO: find a better way to handle timeouts
            #    sys.stderr.write("Connection to server %s failed, trying again after a few seconds...\n" % self.url)
            #    time.sleep(5)
        return features_batch
#b = BerkeleyFeatureGenerator("http://percival.sb.dfki.de:8683", "fr")
#b.parse("C' est notre travail pour continuer à soutenir Lettonie avec l' intégration de la population russe.")
