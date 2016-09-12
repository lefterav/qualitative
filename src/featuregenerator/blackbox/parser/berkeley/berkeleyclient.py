# -*- coding: utf-8 -*-
"""
Feature generator from Berkeley PCFG parses by using a remote Berkeley parsing server
"""

import xmlrpclib 
import time
import logging as log
from featuregenerator import LanguageFeatureGenerator
from featuregenerator.blackbox.parser.berkeley.socketservice.berkeleyparsersocket import BerkeleyParserSocket
from numpy import std, average
import socket

class BerkeleyFeatureGenerator(LanguageFeatureGenerator):

    
    def __init__(self, **kwargs):
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
        if results == {}:
            return {}
        try:
            loglikelihood = results['loglikelihood']
        except:
            loglikelihood = -500
        try:
            nbestList = results['nbest']
        except:
            return {}

        try:
            n = len(nbestList)
        except:
            return {}

        best_confidence = -1e308;
        best_parse = ""
        sum_confidence = 0
        
        confidences = []
        #print "analyzing tree statistics",
        try:
            nbestList = list(nbestList)
        except:
            nbestList = []

        for entry in nbestList:
            try:
                confidence = entry["confidence"]
                confidences.append(float(confidence))
            except:
                return {}
            try:
                parse = entry["tree"]
            except:
                parse = ""
            if float(confidence) > best_confidence:
                best_confidence = float(confidence)
                best_parse = parse
            sum_confidence += float(confidence)
        
        #print
        if confidences == []:
            confidences.append(loglikelihood)
                
        avg_confidence = average(confidences)
        std_confidence = std(confidences)        
        
        features = {}
        features["berkeley-n"] = n
        features["berkley-loglikelihood"] = loglikelihood
        features["berkeley-best-parse-confidence"] = best_confidence
        features["berkeley-avg-confidence"] =  avg_confidence
        features["berkeley-tree"] = best_parse
        features["berkeley-min-confidence"] = min(confidences)
        features["berkeley-std-confidence"] = std_confidence
        if loglikelihood > (avg_confidence + std_confidence): 
            features["berkeley-confidence_high"] = 1
        else:
            features["berkeley-confidence_high"] = 0
        if loglikelihood < (avg_confidence - std_confidence): 
            features["berkeley-loglikelihood_low"] = 1
        else:
            features["berkeley-loglikelihood_low"] = 0
        return features
    
    def prepare_sentence(self, simplesentence):  
        string =  simplesentence.get_string()
        return string
            

class BerkeleyLocalFeatureGenerator(BerkeleyFeatureGenerator):
    """
    Class that handles the feature generation functions by loading Berkeley parser locally 
    through a socketservice connection. This class has the advantage that it gets controlled
    fully by python code. So many parsers can be started and run in parallel, e.g. 
    for speeding up parsing process via parallelization. 
    This may be a problem when parser is too big and can only be loaded once for many
    experiments. In that case use an XMLRPC server    
    """
    
    feature_names = ['berkeley-n', 'berkley-loglikelihood', 'berkeley-best-parse-confidence', 'berkeley-avg-confidence', 
                     'berkeley-tree', 'berkeley-min-confidence', 'berkeley-std-confidence', 'berkeley-confidence_high', 
                     'berkeley-confidence_high', 'berkeley-loglikelihood_low', 'berkeley-loglikelihood_low']

    
    def __init__(self, language=None, grammarfile=None, gateway=None, tokenize=False, **kwargs):
        self.language = language
        self.tokenize = tokenize
        log.info("berkeleyclient: initializing BerkeleyParserSocket")
        self.berkeleyparser = BerkeleyParserSocket(grammarfile, gateway)
        log.info("berkeleyclient: got BParser object")
       
    def parse(self, string):
        log.debug("berkeleyclient: parsing sentence")
        parse = self.berkeleyparser.parse(string)
        return parse
    

class BerkeleyXMLRPCFeatureGenerator(BerkeleyFeatureGenerator):
    def __init__(self, url=None, language="", tokenize = False):
        '''
        Handles the connection with a Berkeley Server through XML-RPC
        '''
        self.server = xmlrpclib.ServerProxy(url)
        self.url = url
        self.language = language
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

        if parallelsentences[0].get_attribute("langsrc") == self.language:
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
        elif  parallelsentences[0].get_attribute("langtgt") == self.language:
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
        return features_batch
