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
                    menu_translator="Lucy",
                    menu_quotes=True, 
                    moses_uri = "http://lns-87247.dfki.uni-sb.de:9200"
                    )
    text = """In the upper right corner of the Panda panel there is an icon in the form of three horizontal lines. Click on "License > Data License"; then click on "Refresh Data". In a few seconds a window appears telling you whether the product has been activated."""
    translation, params = lucy.translate(text)
    for key, value in params.iteritems():
        print key, value
    print translation

    #print lucy._preprocess_menu_items(text)
    