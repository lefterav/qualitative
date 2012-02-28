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
from xml.etree import ElementTree as ET
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator

class IQFeatureGenerator(LanguageFeatureGenerator):
    """
    Handles communication with an Acrolinx IQ server
    @ivar lang:
    @ivar host:
    @ivar user_id:
    @ivar license_data:
    @ivar  
    """
    
    
    def __init__(self, lang, settings = {}, user_id = '1361', host = "msv-3231.sb.dfki.de:8031", wsdl_path = "/acrolinx/services/core-no-mtom?wsdl", protocol = "http"):
        """
        @param lang: abrev. code for the language that this generator will be responsible for
        @type lang: str
        @param host: the hostname (and the port) of the SOAP server
        @type host: str
        @param wsdl_path: the wsdl path of the MTOM service, that needs to be appended to the end of the request url
        @type wsdl_path: str
        @param protocol: the protocol, default value http
        @type protocol: str
        """
        self.lang = lang
        self.host = host
        url = "{0}://{1}{2}".format(protocol, host, wsdl_path)
        self.soap_client = Client(url)
        self.license_data_filename = "license.dat"
        self.user_id = user_id    #if license doesn't work, delete license.dat and change user id OR remove access id
        self._initialize_session(settings)

    def _get_property(self, response, key):
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
    
    def _update_license(self, response):
        """
        Function to call every time we get a response that may change the license. 
        It extracts the license string from the response and updates the text file. 
        Then it returns the license string. 
        This should be called after registerUser or checkDocument
        @return: the license string
        @rtype: str
        """
        license_data_str = self._get_property(response, "license.data")
        license_data_file = open(self.license_data_filename, 'w')
        license_data_file.write(license_data_str)
        license_data_file.close()
        return license_data_str
    
    
    def _read_report_url(self, report_url):
        """
        Processes the xml report by Acrolinx IQ and returns a dict of the corrections suggested
        @param report_xml: the content of the report
        @type report_xml: str
        @return: a dict containing the correction suggested
        @rtype: {str: str}
        @todo: write the function that reads the XML
        """
        feed = urllib.urlopen(report_url)
        tree = ET.parse(feed)
        
        atts = {}
        
        # checking stats
        resStats = tree.find('body/statistics/checkingStats/resultStats')
        
        for item in resStats.attrib.items():
            atts['%s_%s' % (resStats.tag, item[0])] = item[1]
        
        for stat in resStats.getchildren():
            for item in stat.attrib.items():
                atts['%s_%s' % (stat.tag, item[0])] = item[1]
                
        # grammar
        grammar = tree.find('body/results/grammar')
        gLangFlags = grammar.find('listOfLangFlags')
        for gLf in gLangFlags.findall('langFlag'):
            errorName = gLf.find('description').text
            
            # No. of particular errors
            if not 'grammar:%s' % errorName in atts:
                atts['grammar:%s' % errorName] = 1
            else:
                atts['grammar:%s' % errorName] += 1
            
            # No. of matches for particular error
            if not 'grammar:%s_matches' % errorName in atts:
                atts['grammar:%s_matches' % errorName] = len(gLf.findall('match'))
            else:
                atts['grammar:%s_matches' % errorName] += len(gLf.findall('match'))
            
            # No. of chars influenced by particular error
            begin = 999999
            end = 0
            for match in gLf.findall('match'):
                if int(match.get('begin')) < begin: begin = int(match.get('begin'))
                if int(match.get('end')) > end: end = int(match.get('end'))
            diff = end - begin
            if not 'grammar:%s_chars' % errorName in atts:
                atts['grammar:%s_chars' % errorName] = diff
            else:
                atts['grammar:%s_chars' % errorName] += diff
        
        # style
        style = tree.find('body/results/style')
        sLangFlags = style.find('listOfLangFlags')
        for sLf in sLangFlags.findall('langFlag'):
            errorName = sLf.find('description').text
            
            # No. of particular errors
            if not 'style:%s' % errorName in atts:
                atts['style:%s' % errorName] = 1
            else:
                atts['style:%s' % errorName] += 1
            
            # No. of matches for particular error
            if not 'style:%s_matches' % errorName in atts:
                atts['style:%s_matches' % errorName] = len(sLf.findall('match'))
            else:
                atts['style:%s_matches' % errorName] += len(sLf.findall('match'))
            
            # No. of chars influenced by particular error
            begin = 999999
            end = 0
            for match in sLf.findall('match'):
                if int(match.get('begin')) < begin: begin = int(match.get('begin'))
                if int(match.get('end')) > end: end = int(match.get('end'))
            diff = end - begin
            if not 'style:%s_chars' % errorName in atts:
                atts['style:%s_chars' % errorName] = diff
            else:
                atts['style:%s_chars' % errorName] += diff
        
        # make strings from ints
        for item in atts.items():
            atts[item[0]] = str(item[1])
        
        return atts
    
    
    def _attributes2soapproperties(self, attributes = {}):
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
            soap_property = self.soap_client.factory.create('soapProperty')
            soap_property['key'] = key
            soap_property['value'] = value
            soap_properties.append(soap_property)
        return soap_properties   
        
    def _initialize_session(self, settings):
        
        #register only once
        try:
            license_data_file = open(self.license_data_filename, 'r')
            print "reusing stored license"
            license_data_str = license_data_file.readline().strip()
            license_data_file.close()
            
        except IOError:
            
            print "probably new user, obtaining new license"
            # create soapProperty object with user id
            userId = self.soap_client.factory.create('soapProperty')
            userId['key'] = 'user_id'
            userId['value'] = self.user_id
        
            # get licence data string
            register_client_response = self.soap_client.service.registerClient([userId])
            license_data_str = self._update_license(register_client_response)
            
        print license_data_str
        
#        # create soapProperty object with license data
#        # create soapProperty object with license.user_id
        log_in_parameters = {'license.data' : license_data_str 
                           , 'license.user_id' : self.user_id }
        
        log_in_soap_properties = self._attributes2soapproperties(log_in_parameters)
        
#        license_data = self.soap_client.factory.create('soapProperty')
#        license_data['key'] = 'license.data'
#        license_data['value'] = license_data_str
#        
#        userId = self.soap_client.factory.create('soapProperty')
#        userId['key'] = 'license.user_id'
#        userId['value'] = self.user_id
#        
        # get session id
        self.sessionIdStr = self.soap_client.service.requestClientSession(log_in_soap_properties)
        
        #print sessionIdStr
        
            
        # get check id
        self.checkId = self.soap_client.service.getCheckId()
            #print checkId
            
            ### TEXT SETTINGS
        if settings:
            soap_attributes = settings
        else:
            soap_attributes = dict(text_lang = self.lang, 
                                   text_type = 'MT-preediting-DE-EN-T1', 
                                   check_spelling = 'true', 
                                   check_grammar = 'true', 
                                   check_style = 'true',
                                   check_terms = 'MT-preediting-DE-EN-T1.modules.terms',
                                   client_session_id = self.sessionIdStr
                                    )
            
            soap_attributes["license.data"] = license_data_str
            soap_attributes["user.id"] = self.user_id
    
        self.soap_properties = self._attributes2soapproperties(soap_attributes)
        
        
        
    def get_features_string(self, text):
        """
        Receives a text and returns a dict with numerical quality observation features
        @param text: text to be evaluated
        @type text: str
        @return: a dict with attributes retrieved from the quality analysis
        @rtype: {str: str} 
        """
        
        #text = 'Dear clients, we would like to informm you that during the latest commerccial update we recieved marvelous products, which wwe can offers in really good prices. Please keeps in touch for further notice. This break every possibility'
#            text = 'This break every possibility. Dear clients, we would like to informm you that during the latest commerccial update we recieved marvelous products, which wwe can offers in really good prices. Please keeps in touch for further notice. This break every possibility.'
            # encode text to base64
        text64 = base64.standard_b64encode(text)
            
        resp = self.soap_client.service.checkDocumentMtom(self.soap_properties, text64, "utf-8", self.checkId)
        self.license_data_str = self._update_license(resp)
        
        #extract document score from the response
        document_score = self._get_property(resp, "document_score")
        #get url of the report xml
        report_url = self._get_property(resp, "report_url")
        #fix the host part of the url
        report_url = re.sub("://[^/]*/", "://{0}/".format(self.host), report_url)
        print "retrieving report from ", report_url
        #report_xml = urllib.urlopen(report_url).read()
        
        attributes = self._read_report_url(report_url)
        
        return attributes
    
    def get_language_options(self):
        return self.soap_client.service.getLanguageOptions(self.lang)
            
    def __del__(self):
        # release client session in any case
        if self.sessionIdStr:
            self.soap_client.service.releaseClientSession(self.sessionIdStr)
        



#text = 'This break every possibility. Dear clients, we would like to informm you that during the latest commerccial update we recieved marvelous products, which wwe can offers in really good prices. Please keeps in touch for further notice. This break every possibility.'
#ac = IQFeatureGenerator("en")
#print ac.process(text)
