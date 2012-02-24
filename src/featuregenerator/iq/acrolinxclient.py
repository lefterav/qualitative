'''
Created on Feb 24, 2012

@author: jogin
'''
'''
Created on Feb 13, 2012

@author: jogin
'''

#from pysimplesoap.client import SoapClient
#
#url = "http://msv-3231.sb.dfki.de:8031/acrolinx/services/core-no-mtom?wsdl"
#client = SoapClient(wsdl=url, trace=False)
#a = client.ping("")
#print a



from suds.client import Client

# create suds client
url = "http://msv-3231.sb.dfki.de:8031/acrolinx/services/core-no-mtom?wsdl"
soap_client = Client(url)
print soap_client
import base64

#print soap_client
#ping = soap_client.service.ping()
#print ping
#serverId = soap_client.service.getServerId()
#print serverId


license_data_filename = "license.dat"
USER_ID = '1359'   #if license doesn't work, delete license.dat and change user id

def _update_license(response):
    """
    Function to call every time we get a response that may change the license. It extracts the license string from the 
    response and updates the text file. Then it returns the license string.
    @return: the license string
    @rtype: str
    """
    licenseDataStr = response[0]['value']
    license_data_file = open(license_data_filename, 'w')
    license_data_file.write(licenseDataStr)
    license_data_file.close()
    return licenseDataStr


#register only once
try:
    license_data_file = open(license_data_filename, 'r')
    print "reusing stored license"
    licenseDataStr = license_data_file.readline().strip()
    license_data_file.close()
    
except IOError:
    
    print "probably new user, obtaining new license"
    # create soapProperty object with user id
    userId = soap_client.factory.create('soapProperty')
    userId['key'] = 'user_id'
    userId['value'] = USER_ID

    # get licence data string
    register_client_response = soap_client.service.registerClient([userId])
    licenseDataStr = _update_license(register_client_response)
    
print licenseDataStr


# create soapProperty object with license data
licenseData = soap_client.factory.create('soapProperty')
licenseData['key'] = 'license.data'
licenseData['value'] = licenseDataStr

# create soapProperty object with license.user_id
userId = soap_client.factory.create('soapProperty')
userId['key'] = 'license.user_id'
userId['value'] = USER_ID

# get session id
sessionIdStr = soap_client.service.requestClientSession([licenseData, userId])

#print sessionIdStr

# release client session in any case
try:
    # create soapProperty object with client_session_id
    sessionId = soap_client.factory.create('soapProperty')
    sessionId['key'] = 'client_session_id'
    sessionId['value'] = sessionIdStr
    
    # get check id
    checkId = soap_client.service.getCheckId()
    #print checkId
    
    ### TEXT SETTINGS
    
    text = 'Das ist meine Erste versuch.'
    # encode text to base64
    text64 = base64.standard_b64encode(text)
    
    # create soapProperty object with text_lang
    textLang = soap_client.factory.create('soapProperty')
    textLang['key'] = 'text_lang'
    textLang['value'] = 'de'
    
    # create soapProperty object with textType
    textType = soap_client.factory.create('soapProperty')
    textType['key'] = 'text_type'
    textType['value'] = 'MT-preediting-DE-EN'
        
    # create soapProperty object with check_spelling
    checkSpelling = soap_client.factory.create('soapProperty')
    checkSpelling['key'] = 'check_spelling'
    checkSpelling['value'] = 'true'
    
    # create soapProperty object with check_grammar
    checkGrammar = soap_client.factory.create('soapProperty')
    checkGrammar['key'] = 'check_grammar'
    checkGrammar['value'] = 'true'
    
    # create soapProperty object with check_style
    checkStyle = soap_client.factory.create('soapProperty')
    checkStyle['key'] = 'check_style'
    checkStyle['value'] = 'true'
    
    # create soapProperty object with check_terms
    checkTerms = soap_client.factory.create('soapProperty')
    checkTerms['key'] = 'check_terms'
    checkTerms['value'] = 'MT-postediting-DE-EN.modules.terms'
    ###check_terms: comma-separated list of term sets
    
    print soap_client.service.getLanguageOptions('de')
    #aaa
    SOAPProperty = [licenseData, userId, sessionId, \
                    textLang, textType, checkSpelling, checkGrammar, checkStyle]
    print SOAPProperty
    
    resp = soap_client.service.checkDocumentMtom(SOAPProperty, text64, sessionIdStr, checkId)
    print resp
    
finally:
    soap_client.service.releaseClientSession(sessionIdStr)



