'''
Created on Mar 30, 2017

@author: lefterav
'''

from xml.etree.ElementTree import iterparse
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence
import ConfigParser
import sys
from dataprocessor.sax.saxps2jcml import IncrementalJcml

LANGCODE = {'eng': 'en',
            'deu': 'de',
            'ces': 'cs',
            'fin': 'fi',
            'fre': 'fr',
            'rus': 'ru'             
            }

class WMTEvalXmlReader:
    """
    Read Appraise XML output in combination with user ratings as per WMT15
    """
    
    def __init__(self, config):
        """
        Initialize function, by providing a config file with the parameters for data and format
        @param config File object containing a config file of the required format
        @type config: string
        """
        self.config = config
        csvfilename = "%s/%s" % (config.get("data", "path"), config.get("data", "filename"))
        self.xmlfile = open(csvfilename)
        self.judges = {}
        
        
    def get_testset_per_langpair(self, langpair):
        return self.config.get("testsets", langpair)
    
    
    def anonymize_judge(self, judgeID):
        """
        Replace user names with user ids
        @param judgeID: the full name of the user
        @type judgeID: string
        @return: an anonymized user id
        @rtype: string
        """
        if not self.judges.has_key(judgeID):
            self.judges[judgeID] = 'judge%d' % (len(self.judges)+1)
        return self.judges[judgeID]
    
        
    def parse(self):
        """
        Process the XML file and return parallel sentence objects 
        containing text and judgments
        @return: a parallelsentence for each task result
        @rtype: generator of ParallelSentence
        """
        # get an iterable
        context = iterparse(self.xmlfile, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        translations = []
        
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == "HIT":
                hit_id = elem.attrib['hit-id']
                source_language = LANGCODE[elem.attrib['source-language']]
                target_language = LANGCODE[elem.attrib['target-language']]
                testset = self.get_testset_per_langpair("{}-{}".format(source_language, target_language))
            
            if event == "start" and elem.tag == "ranking-task":
                sentence_id = elem.attrib['id']
                source_string = self.extract_source(testset, 
                                                    source_language,
                                                    target_language,
                                                    sentence_id)
                source_sentence = SimpleSentence(source_string, {})
                
                reference_string = self.extract_reference(testset, source_language, target_language, sentence_id)
                reference_sentence = SimpleSentence(reference_string, {})
            
            if event == "start" and elem.tag == "ranking-result":
                user_id = self.anonymize_judge(elem.attrib['user'])
                duration = elem.attrib['duration']
                
            if event == "start" and elem.tag == "translation":
                system_id = elem.attrib['system'].split(",").pop()
                system_id = system_id.replace(".txt", "")
                rank = elem.attrib['rank']
                attributes = {'system_id' : system_id, 'rank' : rank}
                try:
                    translation_string = self.extract_translation(testset,
                                                              source_language,
                                                              target_language,
                                                              sentence_id,
                                                              system_id)
                except Exception as e:
                    print e
                    continue
                
                translation = SimpleSentence(translation_string, attributes)
                translations.append(translation)
            
            if event == "end" and elem.tag == "ranking-task":
                
                attributes = {'judgement_id' : hit_id,
                              'langsrc' : source_language,
                              'langtgt' : target_language,
                              #'file_id' : self.xmlfile.name,
                              'testset' : testset,
                              'user_id' : user_id,
                              'duration' : duration,
                              'id': sentence_id, 
                              }
                parallelsentence = ParallelSentence(source_sentence, 
                                                    translations, 
                                                    reference_sentence, 
                                                    attributes)
                source_sentence = None
                translations = []
                reference_sentence = []
                attributes = {}
                yield parallelsentence
                
    
    def extract_translation(self, testset, source_language, 
                             target_language, sentence_id, system_id):
        """
        Retrieve the text of the system outputs from the respective text files
        @param testset: the name of the test set (e.g. newstest2015)
        """
        langpair = "{}-{}".format(source_language, target_language)
        sentence_index = int(sentence_id)
        sentence_indexing_base = self.config.getint("format","sentence_indexing_base")
        path = self.config.get("data","path")
        result = ''

        if system_id != '_ref':
            pattern_submissions = self.config.get('data', 'pattern_submissions')
            filename = pattern_submissions.format(path=path,
                                                  langpair=langpair,
                                                  testset=testset,
                                                  system=system_id)    
            textfile = open(filename)
            
            index = 0
            for translation_string in textfile:
                if (index + sentence_indexing_base) == sentence_index:
                    result = translation_string
                    break
                index+=1
            textfile.close()
        else:
            result = self.extract_references(target_language, None, sentence_index)
        return result
    
    
    def extract_source(self, testset, source_language, target_language, sentence_id):
        langpair = "{}-{}".format(source_language, target_language)
        sentence_id = int(sentence_id)
        sentence_indexing_base = self.config.getint("format","sentence_indexing_base")
        path = self.config.get("data","path")    
        
        pattern_source = self.config.get("data","pattern_source")
        filename = pattern_source.format(path=path,
                                         langpair=langpair, 
                                         srclang=source_language, 
                                         tgtlang=target_language,
                                         testset=testset)
        
        source_file = open(filename)
        result = ''
        index = 0
        for source_string in source_file:
            if (index + sentence_indexing_base) == sentence_id:
                result = source_string
                break
            index += 1
        if result =='':
            print "Cannot resolve source sentence {} in file {}".format(sentence_id, filename)
        source_file.close()
        return result
    

    def extract_reference(self, testset, source_language, target_language, sentence_id):
        langpair = "{}-{}".format(source_language, target_language)
        sentence_id = int(sentence_id)
        sentence_indexing_base = self.config.getint("format","sentence_indexing_base")
        path = self.config.get("data","path")    
        
        pattern_source = self.config.get("data","pattern_reference")
        filename = pattern_source.format(path=path,
                                         langpair=langpair, 
                                         srclang=source_language, 
                                         tgtlang=target_language,
                                         testset=testset)
        
        reference_file = open(filename)
        result = ''
        index = 0
        for reference_string in reference_file:
            if (index + sentence_indexing_base) == sentence_id:
                result = reference_string
                break
            index += 1
        if result =='':
            print "Cannot resolve source sentence {} in file {}".format(sentence_id, filename)
        reference_file.close()
        return result
    

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print 'USAGE: {} configuration_file.cfg'.format(sys.argv[0])
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        config = ConfigParser.RawConfigParser()
        sys.stderr.write("Opening config file: {}\n".format(sys.argv[1]))
        config.read([sys.argv[1]])
        reader = WMTEvalXmlReader(config)
        parallelsentences = reader.parse()
        writer = IncrementalJcml(config.get("output", "filename"))
        writer.add_parallelsentences(parallelsentences)
        
        
    
                
                