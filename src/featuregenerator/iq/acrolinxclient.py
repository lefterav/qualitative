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
import base64
import re
import urllib

host = "msv-3231.sb.dfki.de:8031"
# create suds client
url = "http://{0}/acrolinx/services/core-no-mtom?wsdl".format(host)
soap_client = Client(url)
print soap_client


#print soap_client
#ping = soap_client.service.ping()
#print ping
#serverId = soap_client.service.getServerId()
#print serverId


license_data_filename = "license.dat"
USER_ID = '1359'   #if license doesn't work, delete license.dat and change user id OR remove access id

def _get_property(response, key):
    """
    Performs a search into the response of the server, 
    and returns the value of a SOAPproperty given its key
    @param response: 
    """
    for soap_property in response:
        if soap_property['key'] == key:
            return soap_property['value']
            break
    return None

def _update_license(response):
    """
    Function to call every time we get a response that may change the license. 
    It extracts the license string from the response and updates the text file. 
    Then it returns the license string. 
    This should be called after registerUser or checkDocument
    @return: the license string
    @rtype: str
    """
    licenseDataStr = _get_property(response, "license.data")
    license_data_file = open(license_data_filename, 'w')
    license_data_file.write(licenseDataStr)
    license_data_file.close()
    return licenseDataStr


def _read_report_xml(report_xml):
    """
    Processes the xml report by Acrolinx IQ and returns a dict of the corrections suggested
    @param report_xml: the content of the report
    @type report_xml: str
    @return: a dict containing the correction suggested
    @rtype: {str: str}
    @todo: write the function that reads the XML
    """
    pass


def _attributes2soapproperties(attributes = {}):
    """
    Converts a normal python dict to a list of SoapProperty instances
    @param attributes: a dict containing soap properties
    @type attributes: {str, str}
    @return: a list of SoapProperty instances that can be sent to Soap
    @rtype: [SoapProperty, ...]
    @todo: replace the handwritten soapProperties with 
    """
    soap_properties = []
    for key, value in attributes.iteritems():
        soap_property = soap_client.factory.create('soapProperty')
        soap_property['key'] = key
        soap_property['value'] = value
        soap_properties.append(soap_property)
    return soap_properties   
    


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
    
    text = 'Dear clients, we would like to informm you that during the latest commerccial update we recieved marvelous products, which wwe can offers in really good prices. Please keeps in touch for further notice. This break every possibility'
    # encode text to base64
    text64 = base64.standard_b64encode(text)
    
    #@todo: replace the following declarations by a dict to be fed to function _attributes2soapproperties
    # create soapProperty object with text_lang
    textLang = soap_client.factory.create('soapProperty')
    textLang['key'] = 'text_lang'
    textLang['value'] = 'en'
    
    # create soapProperty object with textType
    textType = soap_client.factory.create('soapProperty')
    textType['key'] = 'text_type'
    textType['value'] = 'MT-preediting-DE-EN-T1'
        
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
    checkTerms['value'] = 'MT-preediting-DE-EN-T1.modules.terms'
    ###check_terms: comma-separated list of term sets
    
#    print soap_client.service.getLanguageOptions('en')
    #aaa
    soap_properties = [licenseData, userId, sessionId, \
                    textLang, textType, checkSpelling, checkGrammar, checkStyle, checkTerms]
    print soap_properties
    
    resp = soap_client.service.checkDocumentMtom(soap_properties, text64, "utf-8", checkId)
    licenseDataStr = _update_license(resp)
    
    #extract document score from the response
    document_score = _get_property(resp, "document_score")
    #get url of the report xml
    report_url = _get_property(resp, "report_url")
    #fix the host part of the url
    report_url = re.sub("http://[^/]*/", "http://{0}/".format(host), report_url)
    print "retrieving report from ", report_url
    report_xml = urllib.urlopen(report_url).read()
    
    #@todo: write the function that reads that
    attributes = _read_report_xml(report_xml)
    
    
finally:
    soap_client.service.releaseClientSession(sessionIdStr)



