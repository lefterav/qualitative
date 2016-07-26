'''
Created on Sep 13, 2011

@author: Lukas Poustka
'''
import re


class Xml2Mrg:
    """
    Convert xml format of sentence into mrg that is accepted by berkeleyParser.jar.
    """
    def __init__(self, filename):
        """
        All functions that convert xml format to mrg are called.
        """
        xml = self.open_file(filename)
        xml = self.text_part(xml)
        xml = self.comments(xml)
        xml = self.replace_sentence(xml)
        xml = self.punctuation(xml)
        xml = self.pairwise_punctuation(xml, filename)
        xml = self.begin_tags(xml)
        xml = self.end_tags(xml)
        #xml = self.white_spaces(xml)
        self.check_rest_tags(xml)
        self.save_to_file(xml, filename)


    def open_file(self, filename):
        """
        Open input xml.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        a = open(filename, 'r') 
        xml = a.read()
        a.close()
        return xml

    
    def text_part(self, xml):
        """
        Preserve only content inside <TEXT> tags.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        return xml.partition('<TEXT>')[2].partition('</TEXT>')[0]


    def comments(self, xml):
        """
        Remove comments.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        return re.sub('<!--.*?>', '', xml)

    
    def replace_sentence(self, xml):
        """
        Replace sentence tag.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        xml = re.sub('</Sentence>', ')', xml)
        return re.sub('<Sentence .*?Id="[0-9]*">', '(S \n', xml)

    
    def punctuation(self, xml):
        """
        Replace punctuation marks.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        xml = re.sub('<PUNCT.*?PERIOD.*?>', '(. .))', xml)
        xml = re.sub('<PUNCT.*?COMMA.*?>', '(, ,))', xml)
        xml = re.sub('<PUNCT.*?DASH.*?>', '(- -))', xml)
        xml = re.sub('<PUNCT.*?QUOTE.*?>', '(" "))', xml)
        xml = re.sub('<PUNCT.*?COLON.*?>', '(: :))', xml)
        xml = re.sub('<PUNCT.*?SEMICOLON.*?>', '(; ;))', xml)
        xml = re.sub('<PUNCT.*?ELLIPSE.*?>', '(... ...))', xml)
        return xml
        
        
    def pairwise_punctuation(self, xml, filename):
        """
        Punctuation marks that occur in a couple are replaced here.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @param filename: name of input xml file
        @type filename: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        if not xml.count('QUESTION') % 2 == 0: # >?
            print 'Odd number of question marks in %s! Should be even...' % filename
        if not xml.count('EXCLAMATION') % 2 == 0: # <!
            print 'Odd number of exclamation marks in %s! Should be even...' % filename
        if not xml.count('BRACE') % 2 == 0: # {}
            print 'Odd number of brace marks in %s! Should be even...' % filename
        if not xml.count('BRACKET') % 2 == 0: # []
            print 'Odd number of bracket marks in %s! Should be even...' % filename
        if not xml.count('PARENTHESIS') % 2 == 0: # ()
            print 'Odd number of parenthesis marks in %s! Should be even...' % filename
        
        tempXml = ''
        marks = {'QUESTION': ['?-', '-?'], 'EXCLAMATION': ['!-','-!'], 'BRACE': ['{', '}'], \
                  'BRACKET': ['[', ']'], 'PARENTHESIS': ['(', ')']}
        for mark in marks:
            caseN = 0
            for part in re.split('<PUNCT.*?'+mark+'.*?>', xml):
                if caseN == 0:
                    tempXml = part
                elif not caseN % 2 == 0: # odd case
                    tempXml = tempXml + '('+marks[mark][0]+' '+marks[mark][0]+')' + part 
                else: # even case
                    tempXml = tempXml + '('+marks[mark][1]+' '+marks[mark][1]+'))' + part
                caseN += 1
            xml = tempXml

        return xml


    def begin_tags(self, xml):
        """
        Replace beginning tags.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """        
        tagSet = set(re.findall('<[A-Z]+', xml))
        for tag in tagSet:
            xml = re.sub(tag+'.*?>', '('+tag.strip('<'), xml)
        return xml


    def end_tags(self, xml):
        """
        Replace end tags.
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        xml = re.sub('</.*?>', ')', xml)
        return xml


    def white_spaces(self, xml):
        """
        The output file size is minimized to one line. NOT NECESSARY FOR berkeleyParser.jar!
        @param xml: input xml text that is being converted into mrg format
        @type xml: string
        @return xml: input xml text that is being converted into mrg format
        @type xml: string
        """
        xml = re.sub('[\t\n\r\f\v]', '', xml)
        while xml.count('  '):
            xml = re.sub('  ', ' ', xml)
        return xml


    def check_rest_tags(self, xml):
        """
        Check rest tags in converted document. Print warning, if found.
        @param xml: input xml text that has been converted into mrg format
        @type xml: string
        """
        if xml.count('<') or xml.count('>'):
            print 'There are probably still unrecognised tags in the document!'

    
    def save_to_file(self, xml, filename):
        """
        Save the result to the file.
        @param xml: input xml text that has been converted into mrg format
        @type xml: string
        """
        b = open('%s.mrg' % filename.rpartition('.')[0], 'w')
        b.write(xml)
        b.close()

#Xml2Mrg('/media/DATA/Arbeit/DFKI/11_09_08_Penn_format/Berkeley_parser/sample_source_xml_format.xml')
