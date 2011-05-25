# -*- coding: utf-8 -*-

'''
Created on May 25, 2011

@author: elav01
'''
import xmlrpclib, socket, sys
import base64




if __name__ == '__main__':
    s = xmlrpclib.Server("http://134.96.187.4:8585")
    print s.getSentenceProb('This is a cat', 4)
    string = "This is a γάτα"
    #string = unicode(string)
    #string = base64(string)
    print s.getSentenceProb(string)