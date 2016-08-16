'''
Created on 13 Oct 2012

@author: Eleftherios Avramidis
'''

#from ml.ranking import Ranker 
import numpy as np
import logging as log

class PRank:
    '''
    Implements PRank algorithm 
    '''


    def __init__(self, features_count):
        '''
        Constructor
        '''
        self.k = features_count
        
    def train(self, X, Y, iterations=5):
        #TODO: the algorithm should score many ranks altogether
        k = self.k
        #get the size of the featureset
        n = np.size(X, 1);
        #instantiate rule vector w with zeros 
        w = np.zeros(n)
        #instantiate k thresholds b
        B = np.zeros(k)
        #last b should be infinite
        B[k-1] = np.Infinity
        
        #size of training set
        T = np.size(X,0)
        assert (T==np.size(Y,0))
        #assert (np.size(Y,1)==1)
        
        log.debug("Initializing zero vectors\n w={}\tB={}".format(w, B))
       
        #iterate over all training instances
        for i in xrange(iterations):
            log.info("\nIteration {} from {}".format(i+1, iterations))
            for t in xrange(T):
                log.info("\nRound {} from {}".format(t+1, T))
                #get a new rank_strings (featurevector)
                x = X[t]
                #predict 
                wx = np.inner(w, x)
                yp = self._predict_y(wx, B)
                #get a new label
                y = Y[t]
                log.debug("yp = {}, y = {}".format(yp, y))
                if y.all(yp):
                    w, B = self._update_w(k, y, B, wx, w, x)
                log.debug("after correction")
                wx = np.inner(w, x)
                yp = self._predict_y(wx, B)
                log.debug("yp = {}, y = {}".format(yp, y))
        self.w = w
        self.B = B
    
    def _update_w(self, k, y, B, wx, w, x):
        Yr = np.empty(k-1)
        for r in xrange(k-1):
            if y <= r:
                Yr[r] = -1
            else:
                Yr[r] = 1
        log.debug("Y = {}".format(Yr))
        
        tau = np.zeros(k-1)
        for r in xrange(k-1):
            if (wx - B[r]) * Yr[r] <= 0:
                tau[r] = Yr[r]
            else:
                tau[r] = 0
        log.debug("tau = {}".format(tau))
        w = w + np.multiply(np.sum(tau), x)
        for r in xrange(k-1):
            B[r] = B[r] - tau[r]
        log.debug("w = {} B = {}".format(w, B))
        return w, B
                
    def _predict_y(self, wx, B):        
        for r, b in enumerate(B):
            if (wx - b < 0):
                return r
    
    def rank_strings(self, x):
        log.info("decoding")
        wx = np.inner(self.w, x)
        return self._predict_y(wx, self.B)
    
    