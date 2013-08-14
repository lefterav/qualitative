import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:8088')
print s.rank("originaldoc", "mosestranslation", "lucytranslation", "googletranslation", "langsrc", "langtgt")  

# Print list of available methods
