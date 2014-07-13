# -*- coding: utf-8 -*-


import xmlrpclib

s = xmlrpclib.ServerProxy('http://lns-87004.sb.dfki.de:8089')
print s.qualityRank("Das ist eine Entscheidung für mich.", "A decision is this tüp.", "This is a decision .", "This is a very bad decision.", "de", "en")  

# Print list of available methods
