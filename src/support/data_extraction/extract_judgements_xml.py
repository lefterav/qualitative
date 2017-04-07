'''
Created on Mar 30, 2017

@author: lefterav
'''

from xml.etree.ElementTree import iterparse
import ConfigParser
import sys

from dataprocessor.sax.saxps2jcml import MultiLangpairIncrementalWriter
from sentence.sentence import SimpleSentence
from sentence.parallelsentence import ParallelSentence

# global dictionary mapping 3-letter to 2-letter language codes 
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
    @ivar config: the loaded configuration file
    @type config: ConfigParser
    @ivar task: the label of the task in the configuration file
    @type task: string
    @ivar testset: the name of the test set at hand
    @type testset: string
    @ivar xmlfile: the xmlfile to be processed.
    @type xmlfile: file
    @ivar judges: a dictionary mapping the judge names to their anonymized ids
    @type judges: dict(string, string)
    @ivar langpairs: the langpairs whose annotations should be extracted from the given file
    @type langpairs: list of strings
    """
    
    def __init__(self, config, task):
        """
        Initialize function, by providing a config file with the parameters for data and format
        @param config File object containing a config file of the required format
        @type config: string
        @param task: The identifier of the particular task in the config file
        @typte tas: string
        """
        self.config = config
        self.task = task
        path = config.get(self.task, "path")
        self.testset = config.get(self.task, "testset")
        filename = config.get(self.task, "filename").format(path)
        self.xmlfile = open(filename)
        self.judges = {}
        self.langpairs = config.get(self.task, "langpairs").split(",")
    
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
        testset = self.testset
        ignore_hit = False
        
        for event, elem in context:
            #new sentence: get attributes
            if event == "start" and elem.tag == "HIT":
                hit_id = elem.attrib['hit-id']
                source_language = LANGCODE[elem.attrib['source-language']]
                target_language = LANGCODE[elem.attrib['target-language']]
                if "{}-{}".format(source_language, target_language) not in self.langpairs:
                    ignore_hit = True
                else:
                    ignore_hit = False
            
            # Don't parse HITS that don't belong to the desired langpairs
            if ignore_hit:
                continue
            
            # new ranking tasks defines sentence id, chance to get the text of source and reference
            if event == "start" and elem.tag == "ranking-task":
                sentence_id = elem.attrib['id']
                source_string = self.extract_source(testset, source_language, target_language, sentence_id)
                source_sentence = SimpleSentence(source_string, {})
                
                reference_string = self.extract_reference(testset, source_language, target_language, sentence_id)
                reference_sentence = SimpleSentence(reference_string, {})
            
            # result entry provides the duration and the user id
            if event == "start" and elem.tag == "ranking-result":
                user_id = self.anonymize_judge(elem.attrib['user'])
                duration = elem.attrib['duration']
            
            if event == "start" and elem.tag == "translation":
                system_id = elem.attrib['system'].split(",").pop()
                system_id = system_id.replace(".txt", "")
                rank = elem.attrib['rank']
                attributes = {'system_id' : system_id, 'rank' : rank}
                
                try:
                    translation_string = self.extract_translation(testset, source_language, target_language, sentence_id, system_id)
                except Exception as e:
                    if ".tuning-" in str(e):
                        continue
                    else:
                        raise(e)
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
                parallelsentence = ParallelSentence(source_sentence, translations, reference_sentence, attributes)
                source_sentence = None
                translations = []
                reference_sentence = []
                attributes = {}
                yield parallelsentence
                
    def extract_translation(self, testset, source_language, target_language, 
                            sentence_id, system_id):
        """
        Retrieve the text of the system outputs from the respective text files
        @param testset: the name of the test set (e.g. newstest2015)
        @type testset: string
        @param source_language: a 2-letter language code for the source language
        @type source_language: string
        @param target_language: a 2-letter language code for the target language
        @type target_language: string
        @param sentence_id: the id of the sentence to be extracted
        @type sentence_id: string
        @param system_id: the id of the system that produced the sentence
        @type system_id: string
        @return: the text of the translation
        @rtype: string
        """
        langpair = "{}-{}".format(source_language, target_language)
        sentence_index = int(sentence_id)
        sentence_indexing_base = self.config.getint(self.task,"sentence_indexing_base")
        result = ''

        if system_id != '_ref':
            pattern_submissions = self.config.get(self.task, 'pattern_submissions')
            filename = pattern_submissions.format(langpair=langpair, testset=testset, system=system_id)    
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
        """
        Retrieve the text of the source sentence from the external text files 
        for the given sentence id.
        @param testset: the name of the test set (e.g. newstest2015)
        @type testset: string
        @param source_language: a 2-letter language code for the source language
        @type source_language: string
        @param target_language: a 2-letter language code for the target language
        @type target_language: string
        @param sentence_id: the id of the sentence to be extracted
        @type sentence_id: string
        @return: the text of the source sentence
        @rtype: string        
        """        
        langpair = "{}-{}".format(source_language, target_language)
        sentence_id = int(sentence_id)
        sentence_indexing_base = self.config.getint(self.task,"sentence_indexing_base")
        path = self.config.get(self.task,"path")    
        
        pattern_source = self.config.get(self.task,"pattern_source")
        filename = pattern_source.format(langpair=langpair, 
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
        """
        Retrieve the text of the reference translation from the external text files 
        for the given sentence id.
        @param testset: the name of the test set (e.g. newstest2015)
        @type testset: string
        @param source_language: a 2-letter language code for the source language
        @type source_language: string
        @param target_language: a 2-letter language code for the target language
        @type target_language: string
        @param sentence_id: the id of the sentence to be extracted
        @type sentence_id: string
        @return: the text of the reference translation
        @rtype: string        
        """             
        langpair = "{}-{}".format(source_language, target_language)
        sentence_id = int(sentence_id)
        sentence_indexing_base = self.config.getint(self.task,"sentence_indexing_base")
        path = self.config.get(self.task,"path")    
        
        pattern_source = self.config.get(self.task,"pattern_reference")
        filename = pattern_source.format(langpair=langpair, 
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


def _read_configuration():
    config = ConfigParser.ConfigParser()
    sys.stderr.write("Opening config file: {}\n".format(sys.argv[1]))
    config.read([sys.argv[1]])
    return config

def process_tasks(config):
    tasks = [section for section in config.sections() if section.startswith("task:")]
    print tasks
    for task in tasks:
        print "Starting", task
        
        if config.get(task, "reader_mode") == "xml":
            reader = WMTEvalXmlReader(config, task)
            
        else: 
            reader = None
        parallelsentences = reader.parse()
        
        langpairs = config.get(task, "langpairs").split(",")
        output_pattern = config.get(task, "pattern_output")
        writer = MultiLangpairIncrementalWriter(langpairs, output_pattern)
        writer.add_parallelsentences(parallelsentences)
        print "Finished ", task


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print 'USAGE: {} CONFIGURATION_FILES'.format(sys.argv[0])
        #print 'USAGE: %s SORTEDJUDGMENTS.CSV PATH' % sys.argv[0]
        #print '\tpath = path to folder with evaluation raw data'
    else:
        config = _read_configuration()
        process_tasks(config)
        
        
        
    
                
                