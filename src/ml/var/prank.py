'''
Created on 13 Oct 2012

@author: Eleftherios Avramidis
'''

from classifier import Classifier
import numpy as np
import logging

class PRank(Classifier):
    '''
    Implements PRank algorithm 
    '''


    def __init__(self, k):
        '''
        Constructor
        '''
        self.k = k 
        
    def learn(self, X, Y, iterations):
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
        assert (np.size(Y,1)==1)
        
        logging.debug("Initializing zero vectors\n w={}\tB={}".format(w, B))
       
        #iterate over all training instances
        for i in xrange(iterations):
            logging.info("\nIteration {} from {}".format(i+1, iterations))
            for t in xrange(T):
                logging.info("\nRound {} from {}".format(t+1, T))
                #get a new rank (featurevector)
                x = X[t]
                #predict 
                wx = np.inner(w, x)
                yp = self.predict_y(wx, B)
                #get a new label
                y = Y[t,0]
                print "yp =",yp, ", y =",y
                if y != yp:
                    w, B = self.update_w(k, y, B, wx, w, x)
                print "after correction"
                wx = np.inner(w, x)
                yp = self.predict_y(wx, B)
                print "yp =",yp, ", y =",y
        self.w = w
        self.B = B
    
    def update_w(self, k, y, B, wx, w, x):
        Yr = np.empty(k-1)
        for r in xrange(k-1):
            if y <= r:
                Yr[r] = -1
            else:
                Yr[r] = 1
        print "Y =", Yr
        
        tau = np.zeros(k-1)
        for r in xrange(k-1):
            if (wx - B[r]) * Yr[r] <= 0:
                tau[r] = Yr[r]
            else:
                tau[r] = 0
        print "tau =", tau
        w = w + np.multiply(np.sum(tau), x)
        for r in xrange(k-1):
            B[r] = B[r] - tau[r]
        print "w={} B={}".format(w, B)
        return w, B
                
            
            
    def predict_y(self, wx, B):        

        for r, b in enumerate(B):
            if (wx - b < 0):
                return r
    
    
    def rank(self, x):
        print "decoding"
        wx = np.inner(self.w, x)
        return self.predict_y(wx, self.B)
    
if __name__ == '__main__':
    traindata = np.array([[1, 1, 1, 1, 1],
                          
                          [0.5, 1, 2, 1, 3],
                          [1, 1, 1, 0, 0],
                          [1, 1, 0, 0, 0],
                          ])
    
    labels = np.array([[0],
                       [1],
                       [2],
                       [3],
                                       
                       
                      ])
    k = len(set(labels[:,0]))
    ranker = PRank(k)
    ranker.learn(traindata, labels)
    testdata = np.array([1.1, 1, 0, 0, 1])
    print ranker.rank(testdata)