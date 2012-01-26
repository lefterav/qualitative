'''
Created on 15 Σεπ 2011

@author: lefterav
'''

import xmlrpclib 
import time
import sys
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
import socket

class BerkeleyFeatures():
    '''
    Handles the connection with a Berkeley Server 
    '''


    def __init__(self, url, lang=""):
        '''
        Constructor
        '''
        self.server = xmlrpclib.Server(url)
        self.url = url
        self.lang = lang
    

    #Warning: not language-aware function. Use the ones above
    def get_features_simplesentence(self, sent_string):
        
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
        attributes ["berkley-loglikelihood"] = str(results['loglikelihood'])
        attributes ["berkeley-best-parse-confidence"] = str(best_confidence)
        attributes ["berkeley-avg-confidence"] = str(avg_confidence)
        attributes ["berkeley-tree"] = best_parse
        return attributes
    
    
    def xmlrpc_call(self, batch):
        socket.setdefaulttimeout(None) 
        connected = False
        features_batch = []
        while not connected:
            try:
                features_batch = self.server.BParser.parse_batch(batch)
                connected = True
            except:
                time.sleep(5)
            #except TimeoutException: TODO: find a better way to handle timeouts
            #    sys.stderr.write("Connection to server %s failed, trying again after a few seconds...\n" % self.url)
            #    time.sleep(5)
        return features_batch
