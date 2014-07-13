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
import sys
from urllib2 import URLError
from xml.etree import ElementTree as ET
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
import os
import time

class IQFeatureGenerator(LanguageFeatureGenerator):
    """
    Handles communication with an Acrolinx IQ server
    @ivar lang:
    @ivar host:
    @ivar user_id:
    @ivar license_data:
    @ivar  
    """
    
    
    def __init__(self, lang, settings = {}, user_id = 'dfkitaraxu', host = "msv-3231.sb.dfki.de:8031", wsdl_path = "/acrolinx/services/core-no-mtom?wsdl", protocol = "http" , license_file = "license.dat"):
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
        self.soap_client = Client(url, timeout=60)
        license_file = "{}.dat".format(user_id)
        path = os.path.dirname(__file__) #keep license file in current directory for the moment
        self.license_data_filename = os.path.join(path, license_file)
        
        self.user_id = user_id    #if license doesn't work, delete license.dat and change user id OR remove access id
        self.settings = settings
        print "proceeding with IQ session initialization"
        self._initialize_session()

    def _get_property(self, response, key):
        """
        Performs a search into the response of the server, 
        and returns the value of a SOAPproperty given its key
        @param response: 
        """
        for soap_property in response:
            if soap_property['key'] == key:
                return soap_property['value']
        raise KeyError
    
    def _update_license(self, response):
        """
        Function to call every time we get a response that may change the license. 
        It extracts the license string from the response and updates the text file. 
        Then it returns the license string. 
        This should be called after registerUser or checkDocument
        @return: the license string
        @rtype: str
        """
        self.license_data_str = self._get_property(response, "license.data")
        license_data_file = open(self.license_data_filename, 'w')
        license_data_file.write(self.license_data_str)
        license_data_file.close()
        return self.license_data_str
    
    
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
            errorName = errorName.replace(" ", "_")
            errorName = errorName.replace(":", "_")
            
            # No. of particular errors
            if not 'grammar_%s' % errorName in atts:
                atts['grammar_%s' % errorName] = 1
            else:
                atts['grammar_%s' % errorName] += 1
            
            # No. of matches for particular error
            if not 'grammar_%s_matches' % errorName in atts:
                atts['grammar_%s_matches' % errorName] = len(gLf.findall('match'))
            else:
                atts['grammar_%s_matches' % errorName] += len(gLf.findall('match'))
            
            # No. of chars influenced by particular error
            begin = 999999
            end = 0
            for match in gLf.findall('match'):
                if int(match.get('begin')) < begin: begin = int(match.get('begin'))
                if int(match.get('end')) > end: end = int(match.get('end'))
            diff = end - begin
            if not 'grammar_%s_chars' % errorName in atts:
                atts['grammar_%s_chars' % errorName] = diff
            else:
                atts['grammar_%s_chars' % errorName] += diff
        
        # style
        style = tree.find('body/results/style')
        sLangFlags = style.find('listOfLangFlags')
        for sLf in sLangFlags.findall('langFlag'):
            errorName = sLf.find('description').text
            
            if errorName.startswith("Sentence too long"):
                too_long = re.findall("Sentence too long\: (\d*)", errorName)[0] 
                errorName = "style_too_long"
                atts['style_too_long'] = too_long 
            else:
                errorName = errorName.replace(" ", "_")
                errorName = errorName.replace(":", "_")
                # No. of particular errors
                if not 'style_%s' % errorName in atts:
                    atts['style_%s' % errorName] = 1
                else:
                    atts['style_%s' % errorName] += 1
            
            # No. of matches for particular error
            if not 'style_%s_matches' % errorName in atts:
                atts['style_%s_matches' % errorName] = len(sLf.findall('match'))
            else:
                atts['style_%s_matches' % errorName] += len(sLf.findall('match'))
            
            # No. of chars influenced by particular error
            begin = 999999
            end = 0
            for match in sLf.findall('match'):
                if int(match.get('begin')) < begin: begin = int(match.get('begin'))
                if int(match.get('end')) > end: end = int(match.get('end'))
            diff = end - begin
            if not 'style_%s_chars' % errorName in atts:
                atts['style_%s_chars' % errorName] = diff
            else:
                atts['style_%s_chars' % errorName] += diff
        
        # make strings from ints
        for item in atts.items():
            atts[item[0]] = str(item[1])
        
        return atts
    
    
    def _attributes2soapproperties(self, attributes = {}):
        """
        Converts a normal python dict to a list of SoapProperty instances
        @param attrib    utes: a dict containing soap properties
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
        
    def _initialize_session(self):
        settings = self.settings
        #register only once
        try:
            license_data_file = open(self.license_data_filename, 'r')
            print "reusing stored license"
            self.license_data_str = license_data_file.readline().strip()
            license_data_file.close()
            
        except IOError:
            
            print "probably new user, obtaining new license"
            # create soapProperty object with user id
            userId = self.soap_client.factory.create('soapProperty')
            userId['key'] = 'user_id'
            userId['value'] = self.user_id
        
            # get licence data string
            print "trying to register client with userid", userId
            register_client_response = self.soap_client.service.registerClient([userId])
            self._update_license(register_client_response)
            
        print self.license_data_str
        
#        # create soapProperty object with license data
#        # create soapProperty object with license.user_id
        log_in_parameters = {'license.data' : self.license_data_str 
                           , 'license.user_id' : self.user_id }
        
        log_in_soap_properties = self._attributes2soapproperties(log_in_parameters)
#        
        # get session id
        print "trying get session by giving properties ", log_in_soap_properties
        
        connected = False
        while not connected:
            try:
                self.sessionIdStr = self.soap_client.service.requestClientSession(log_in_soap_properties)
                connected = True
            except URLError:
                sys.stderr.write("UrlError on initializing suds client. Trying again\n")
                time.sleep(5)        
                
            
        
        #print sessionIdStr
        
    def _start_new_check(self):
        # get check id
        settings = self.settings
#        print "getting required check id"
        check_id = self.soap_client.service.getCheckId()

        if settings:
            soap_attributes = settings
        else:
            soap_attributes = dict(
                                   text_type = 'MT-preediting-DE-EN-T1', 
                                   check_spelling = 'true', 
                                   check_grammar = 'true', 
                                   check_style = 'true',
                                   check_terms = 'MT-preediting-DE-EN-T1.modules.terms',
                                    )
        license_data_str = open(self.license_data_filename, 'r').read()
        soap_attributes["text_lang"] = self.lang
        soap_attributes["client_session_id"] = self.sessionIdStr
        soap_attributes["license.data"] = license_data_str
        soap_attributes["user.id"] = self.user_id
    
        soap_properties = self._attributes2soapproperties(soap_attributes)
        return check_id, soap_properties
        
        
        
    def get_features_string(self, text):
        """
        Receives a text and returns a dict with numerical quality observation features
        @param text: text to be evaluated
        @type text: str
        @return: a dict with attributes retrieved from the quality analysis
        @rtype: {str: str} 
        """
        
        tries_resp = 0
        resp = None
        while not resp:
            tries = 0
            check_id = None
            while not check_id:
                text64 = base64.standard_b64encode(text)
                try:
                    check_id, soap_properties = self._start_new_check()
                except Exception as inst:
                    check_id = None
                    sys.stderr.write("\nWhile getting check ID, server reported error: {}\n".format(inst))
                    tries += 1
                    if tries > 5:
                        raise inst
                    time.sleep(20)
                    sys.stderr.write("retrying...")
    #            print 'soap_properties', soap_properties
    #            print 'text64', text64
    #            print 'check_id', check_id
    #            print 'resp = self.soap_client.service.checkDocumentMtom(soap_properties, text64, "utf-8", check_id)'
    #       
            try:
                resp = self.soap_client.service.checkDocumentMtom(soap_properties, text64, "utf-8", check_id)
            except Exception as inst:
                resp = None
                sys.stderr.write("\nWhen submitted sentence, server reported error: {}\n".format(inst))
                sys.stderr.write("original sentence: {}\n".format(text))
                sys.stderr.write("b64 encoded sentence: {}\n".format(text64))
                tries_resp += 1
                if tries_resp > 5:
                    raise inst
                time.sleep(20)
                sys.stderr.write("retrying...")
            
        
        self._update_license(resp)
        
        #extract document score from the response
        document_score = self._get_property(resp, "document_score")
        #get url of the report xml
        report_url = self._get_property(resp, "report_url")
        #fix the host part of the url
        report_url = re.sub("://[^/]*/", "://{0}/".format(self.host), report_url)
        #print "retrieving report from ", report_url
        #report_xml = urllib.urlopen(report_url).read()
        
        attributes = self._read_report_url(report_url)
        print ".",
        return attributes
            
    
    def get_language_options(self):
        return self.soap_client.service.getLanguageOptions(self.lang)
            
    def __del__(self):
        try:
            self.soap_client.service.releaseClientSession(self.sessionIdStr)
        except:
            pass
#        # release client session in any case
        

#
#
if __name__ == '__main__':
    
    text = 'This break every possibility. Dear clients, we would like to informm you that during the latest commerccial update we recieved marvelous products, which wwe can offers in really good prices. Please keeps in touch for further notice. This break every possibility.'
    ac = IQFeatureGenerator("en")
from dataprocessor.sax import saxjcml
    #
    saxjcml.run_features_generator("/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training.jcml", 
                                   "/home/Eleftherios Avramidis/taraxu_data/wmt12/qe/training_set/training.iq.jcml", [ac])
    print ac.process(text)
