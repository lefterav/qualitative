# -*- coding: utf-8 -*-
'''
Created on 19 Apr 2016

@author: Eleftherios Avramidis
'''
from mt.lucy import LucyWorker, AdvancedLucyWorker
import logging

if __name__ == '__main__':
    
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
    
    lucy = AdvancedLucyWorker(url='http://msv-3251.sb.dfki.de:8080/AutoTranslateRS/V1.2/mtrans/exec',
                      source_language="en",
                      target_language="de",
                      unknowns=True,
                      moses_uri = "http://lns-87247.dfki.uni-sb.de:9200"
                      )
    translation, params = lucy.translate('You can view this information by going to View> Summary ...')
    print translation
    for key, value in params.iteritems():
        print key, value
        