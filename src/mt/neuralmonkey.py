from featuregenerator.sentencesplitter import SentenceSplitter
from featuregenerator.preprocessor import Normalizer, Tokenizer, Truecaser,\
    CompoundSplitter, Detruecaser, Detokenizer
import requests

class NeuralMonkeyWorker:
    """
    Wrapper class for another worker, that also takes care of pre-processing the given requests
    and post-processing the output.
    @ivar worker: an initialized worker that connects to a MT engine
    @type worker: L{Worker}
    @ivar sentencesplitter: the class for splitting sentences
    @type sentencesplitter: L{SentenceSplitter}
    @ivar preprocessors: a list of pre-processors
    @type preprocessors: list of L{Preprocessor}
    @ivar postprocessors: a list of post-processors
    @type postprocessors: list of L{Postprocessor}
    """
    def __init__(self, uri, source_language, target_language, 
                 truecaser_model, splitter_model=None, worker=None, **kwargs):
        
        self.sentencesplitter = SentenceSplitter({'language': source_language})
        self.preprocessors = [Normalizer(language=source_language),
                              Tokenizer(language=source_language),
                              Truecaser(language=source_language, 
                                        filename=truecaser_model),
                              ]
        if source_language == 'de' and splitter_model:
            self.preprocessors.append(CompoundSplitter(language=source_language,
                                                       filename=splitter_model))
        self.postprocessors = [Detruecaser(language=target_language),
                               Detokenizer(language=target_language)]
        self.uri = uri
        self.name = "neuralmonkey"
        
        
    def translate(self, string):
        strings = self.sentencesplitter.split_sentences(string)
        
        preprocessed_strings = []
        for string in strings:
            for preprocessor in self.preprocessors:
                string = preprocessor.process_string(string)
            preprocessed_strings.append(string.split())
        
        request = {"source": preprocessed_strings}
        response = requests.post(self.uri, json=request)
        translated_token_lists = response.json()['target']
        
        translated_strings = []
        for translated_token_list in translated_token_lists:
            translated_string = " ".join(translated_token_list)
            for postprocessor in self.postprocessors:
                translated_string = postprocessor.process_string(translated_string)
            translated_strings.append(translated_string)
        
        return " ".join(translated_strings), response.text
            