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

#print soap_client
#ping = soap_client.service.ping()
#print ping
#serverId = soap_client.service.getServerId()
#print serverId

# create soapProperty object with user id
userId = soap_client.factory.create('soapProperty')
userId['key'] = 'user_id'
userId['value'] = '1393'

# get licence data string
licenseDataStr = soap_client.service.registerClient([userId])[0]['value']
#print licenseDataStr

# create soapProperty object with license data
licenseData = soap_client.factory.create('soapProperty')
licenseData['key'] = 'license.data'
licenseData['value'] = licenseDataStr

# create soapProperty object with license.user_id
userId = soap_client.factory.create('soapProperty')
userId['key'] = 'license.user_id'
userId['value'] = '1393'

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
    text64 = text.encode('base64', 'strict')
    
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
    checkTerms['value'] = 'MT-preediting-DE-EN.modules.terms'
    ###check_terms: comma-separated list of term sets
    
    print soap_client.service.getLanguageOptions('de')
    #aaa
    SOAPProperty = [licenseData, userId, sessionId, \
                    textLang, textType, checkSpelling, checkGrammar, checkStyle, checkTerms]
    print SOAPProperty
    
    resp = soap_client.service.checkDocumentMtom(SOAPProperty, text64, sessionIdStr, checkId)
    print resp
finally:
    soap_client.service.releaseClientSession(sessionIdStr)



