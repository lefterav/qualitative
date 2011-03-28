import xmlrpclib 
import base64
from featuregenerator.featuregenerator import FeatureGenerator
from nltk.tokenize.punkt import PunktWordTokenizer

class SRILMUnknownWord(FeatureGenerator):
    '''
    Gets all the words of a sentence through a SRILM language model and counts how many of them are unknown (unigram prob -99) 
    '''
    
    def __init__(self, url, lang="en", lowercase=True, tokenize=True):
        '''
        Define connection with the server
        '''
        self.server = xmlrpclib.Server(url)
        self.lang = lang
        self.lowercase = lowercase
        self.tokenize = tokenize
        
    
    def add_features_src(self, simplesentence, parallelsentence):
        src_lang = parallelsentence.get_attribute("langsrc")
        if src_lang == self.lang:
            simplesentence = self.__process__(simplesentence)

        return simplesentence

    def add_features_tgt(self, simplesentence, parallelsentence):
        tgt_lang = parallelsentence.get_attribute("langtgt")
        if tgt_lang == self.lang:
            simplesentence = self.__process__(simplesentence)
        return simplesentence        
    
    
    def __prepare_sentence__(self, simplesentence):
        sent_string = simplesentence.get_string().strip()
        if self.tokenize:
            tokenized_string = PunktWordTokenizer().tokenize(sent_string)
            sent_string = ' '.join(tokenized_string)
        else:
            tokenized_string = sent_string.split(' ')
            
        if self.lowercase:
            sent_string = sent_string.lower()
        return (tokenized_string,sent_string)
    
    
    def __process__(self, simplesentence):
        (tokens,sent_string) = self.__prepare_sentence__(simplesentence)
        unk_count = 0
        uni_probs = 1
        bi_probs = 1
        tri_probs = 1
        unk_tokens = []
        
        #check for unknown words and collecting unigram probabilities:
        for token in tokens:
            uni_prob = self.server.getUnigramProb(base64.standard_b64encode(token))
            if uni_prob == -99:
                unk_count += 1
                unk_tokens.append(token)
            else:
                uni_probs *= uni_prob
        
        #get bigram probabilities
        for pos in range ( len(tokens) -1 ):
            token = tokens[pos:pos+1]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens):
                bi_prob = self.server.getBigramProb(base64.standard_b64encode(token))
                bi_probs *= bi_prob
         
        #get trigram probabilities
        for pos in range ( len(tokens) -2 ):
            token = tokens[pos:pos+2]
            if (token[0] not in unk_tokens) and (token[1] not in unk_tokens) and (token[2] not in unk_tokens):
                tri_prob = self.server.getTrigramProb(base64.standard_b64encode(token))
                tri_probs *= tri_prob
        
        attributes = { 'unk' : str(unk_count),
                       'uni-prob' : str(uni_prob),
                       'bi-prob' : str(bi_prob),
                       'tri-prob' : str(tri_prob) }
        
        simplesentence.add_attributes(attributes)
        return simplesentence
            
            
    
    
    def __get_sentence_probability__(self, sent_string ):
        
        l = len(sent_string.split(" "))       
   
        #print l, sent_string
        return str (self.server.getSentenceProb(base64.standard_b64encode(sent_string), l))
        
