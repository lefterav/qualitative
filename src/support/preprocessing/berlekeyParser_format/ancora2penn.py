'''
Created on Oct 5, 2011

@author: Lukas Poustka
'''
import os
import re


class Ancora2Penn:
    """
    Convert xml format of sentence into penn that is accepted by berkeleyParser.jar.
    """
    def __init__(self, filename):
        """
        All functions that convert xml format to penn are called from here.
        """
        xml = self.open_file(filename)
        xml = self.trash_and_comments(xml)
        xml = self.set_bounds_to_snt_unit(xml)
        xml = self.punctuation(xml)
        xml = self.words(xml)
        xml = self.begin_tags(xml)
        xml = self.end_tags(xml)
        xml = self.white_spaces(xml)
        xml = self.separate_snts(xml)
        self.check_correctness(xml)
        self.save_to_file(xml, filename)
    
    
    def open_file(self, filename):
        """
        Open input xml.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
        @type xml: string
        """
        a = open(filename, 'r') 
        xml = a.read()
        a.close()
        return xml
    
    
    def trash_and_comments(self, xml):
        """
        Remove comments.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
        @type xml: string
        """
        # remove xml-file head
        xml = re.sub('<.xml.*?>', '', xml)

        # remove comments
        xml = re.sub('(?s)<!--.*?>', '', xml)
        
        # remove article tags
        xml = re.sub('<article.*?>', '', xml)
        xml = re.sub('</article>', '', xml)
        
        # remove empty sentences (sentence without words)
        for sent in set(re.findall('(?s)<sentence.*?</sentence>', xml)):
            if not sent.count('wd="'):
                xml = xml.replace(sent, '')
        
        # remove begin-end tags
        # begin-end tags occur here only as <sn ... /> type
        # I don't know the meaning of this tag...
        tagSet = set(re.findall('<sn+.*?/\s*>', xml))
        for tag in tagSet:
            xml = xml.replace(tag, '')
        return xml
    


        
        return xml
    
    
    def set_bounds_to_snt_unit(self, xml):
        # this function creates 2 bracket in the beginning and in the end of each sentence
        
        # begin of sentence
        xml = re.sub('<sentence.*?>', '((sentence', xml)
        
        # end of sentence; #newline# is later replaced by '\n\n'
        xml = re.sub('</sentence>', '))#newline#', xml)
        
        return xml
    
    
    def punctuation(self, xml):
        """
        Replace punctuation marks.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
        @type xml: string
        """
        
        for punc in set(re.findall('<f .*?>', xml)):
            lem = punc.partition('lem="')[2].partition('"')[0]
            if lem == '(': # replace '(' by '{'
                xml = xml.replace(punc, '({ {)')
            elif lem == ')': # replace ')' by '}'
                xml = xml.replace(punc, '(} })')
            else:
                xml = xml.replace(punc, '(pu %s)' % lem)

        return xml
    
    
    def words(self, xml):
        """
        Extract words and tag name from tags with words.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
        @type xml: string
        """
        tagSetWords = set(re.findall('<.*?wd=".*?>', xml))
        for tag in tagSetWords:
            tagName = re.findall('<[A-Za-z.]+', tag)[0].strip('<')
            word = re.findall('wd=".*?"', tag)[0].strip('wd=').strip('"')
            
            # replace space with underline, if space occurs inside the word
            if word.count(' '): word = word.replace(' ','_')
            
            # remove round bracket, if they occur inside the word
            if word.count('(') or word.count(')'): word = word.replace('(','').replace(')','')
            
            xml = xml.replace(tag, '(%s %s)' % (tagName, word))
        
        # replace ampersand quotation; MUST be behind for loop in words!
        xml = xml.replace('&quot;', '"')
        
        return xml
    
    
    def begin_tags(self, xml):
        """
        Replace beginning tags.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
        @type xml: string
        """        
        tagSet = set(re.findall('<[A-Za-z.]+', xml))
        for tag in tagSet:
            xml = re.sub(tag+'.*?>', '('+tag.strip('<'), xml)
        return xml
    

    def end_tags(self, xml):
        """
        Replace end tags.
        @param xml: input xml text that is being converted into penn format
        @type xml: string
        @return xml: input xml text that is being converted into penn format
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
        
        # remove dots
        #print len(xml)
        #dots_set = set(re.findall('\w\.\w', xml))
        #print dots_set
        #for dot in dots_set:
        #    xml = xml.replace(dot, dot[0]+dot[2])
        #print len(xml)
        
        return xml


    def separate_snts(self, xml):
        return re.sub('#newline#', '\n', xml)
    
    
    def check_correctness(self, xml):
        """
        Check rest tags in converted document. Print warning, if found.
        Check bracket balance. Print warning, if found. 
        @param xml: input xml text that has been converted into penn format
        @type xml: string
        """
        if xml.count('<') or xml.count('>'):
            print 'There are probably still unrecognised tags in the file!'
        if xml.count('(') <> xml.count(')'):
            print 'Number of bracket is unbalanced in the file!'
            print 'No. of left brackets: %s' % str(xml.count('('))
            print 'No. of right brackets: %s' % str(xml.count(')'))    

    
    def save_to_file(self, xml, filename):
        """
        Save the result to the file.
        @param xml: input xml text that has been converted into penn format
        @type xml: string
        """
        dest = '%s.mrg' % filename.rpartition('.')[0]
        b = open(dest, 'w')
        b.write(xml)
        b.close()
        #print 'File in penn format was saved to %s' % dest

# generate mrg
generateMrg = True
if generateMrg:
    addr = '/media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/ancora-2.0/'
    dirs = ['3LB-CAST/', 'CESS-CAST-A/', 'CESS-CAST-AA/', 'CESS-CAST-P/']
    f = 0
    for dir in dirs:
        for filename in os.listdir(addr+dir):
            if filename.endswith('.xml'):
                f += 1 
                Ancora2Penn(addr+dir+filename)
                print f, '\t', filename

# merging files
merge = True
if merge:
    print '\n----------merging:----------'
    addr2 = '/media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/testing_sample/'
    outFilename = 'output.mrg'
    out = open(addr2+outFilename, 'w')
    f = 0
    for dir in dirs:
        for filename in os.listdir(addr+dir):
            if filename.endswith('.mrg'):
                inp = open(addr+dir+filename, 'r')
                out.write(inp.read()+'\n')
                inp.close()
                f += 1
                print f, '\t', filename, 'merged to', outFilename 
    out.close()


# get statictics
statistics = False
if statistics:
    print '\n----------statistics:----------'
    addr3 = '/media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/testing_sample/'
    a = open(addr3+'pennTreesX.mrg', 'r')
    penn = a.read()
    print penn.count('('), penn.count(')')
    a.close()

# delete temporary mrg files
deleteFiles = True
if deleteFiles:
    print '\n----------deleting:----------'
    addr = '/media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/ancora-2.0/'
    dirs = ['CESS-CAST-P/', '3LB-CAST/', 'CESS-CAST-A/', 'CESS-CAST-AA/']
    f = 1
    for dir in dirs:
        for filename in os.listdir(addr+dir):
            if filename.endswith('.mrg'):
                os.remove(addr+dir+filename)
                print f, '\t', filename, 'was deleted!'
                f += 1

# launching cmdline
cmdline = True
if cmdline:
    print '\n---------launching cmdline:----------'
    cmd = 'java -cp /media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/testing_sample/berkeleyParser.jar edu.berkeley.nlp.PCFGLA.GrammarTrainer -path /media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/testing_sample/output.mrg -out /media/DATA/Arbeit/DFKI/11_10_04_SpanishTreebankAncora2Penn/testing_sample/result/Spanish.gr -treebank SINGLEFILE'
    os.system(cmd)
