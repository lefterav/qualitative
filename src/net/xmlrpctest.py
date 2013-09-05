import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:8089')
print s.qualityRank("Das ist eine Entscheidung.", "A decision is this.", "This is a decision .", "This is a very bad decision.", "de", "en")  

# Print list of available methods
