import ijson
import re
import urllib2


def get_token_senses(sentence):
    token_senses = {}
    characters_covered = {}
    for token in sentence["annotations"]:
        token_sense = token["senses"][0] #take only first sense
        #TODO: clean token sense
        token_sense, probability = re.findall("bn:(\d*)n\(([^(]*)\)", token_sense)[0]
        start = token["stringStart"]
        end = token["stringEnd"]
        
        token_covered = False
        for i in range(start, end):
            if i in characters_covered:
                token_covered = True
                break
            else: 
                characters_covered[i] = True
        
        if token_covered:
            continue
        else:
            token_senses[start] = (token_sense, end)
    return token_senses


def read_wsd_output(sentence, sentence_string):
    token_senses = get_token_senses(sentence)
    #print token_senses
    
    token = []
    tokens = sentence_string.split()
    token_start = 0
    mixed_string = []
    replace_string = []

    sense_end = float("-Inf")     

    token_sense = "-"
    bn_token_sense = "-"

    for token in tokens:
        token_end = token_start + len(token) 

        if token_start > sense_end:
            sense_end = float("-Inf")                    

        if token_start <= sense_end:
            rest_string = ""
            mixed_string.append("{}|{}".format(token[:sense_end-token_start], token_sense))
            if (replace_string and replace_string[-1]!=bn_token_sense) or not replace_string:                 
                replace_string.append(bn_token_sense)
            if sense_end-token_start < len(token):
                rest_string = token[sense_end-token_start:]
                mixed_string.append("{}|-".format(rest_string))
                replace_string.append(rest_string)

        elif token_start in token_senses:
            token_sense, sense_end = token_senses[token_start]
            bn_token_sense ="bn:{}n".format(token_sense)
            #sense_end = c.tokenize_offset(sense_end)
            mixed_string.append("{}|{}".format(token[:sense_end-token_start], token_sense))
            if (replace_string and replace_string[-1]!=bn_token_sense) or not replace_string:                 
                replace_string.append(bn_token_sense)
            if sense_end-token_start < len(token):
                rest_string = token[sense_end-token_start:]
                mixed_string.append("{}|-".format(rest_string))
                replace_string.append(rest_string)

        else:
            mixed_string.append("{}|-".format(token))
            replace_string.append("{}".format(token))
        token_start = token_end+1
    return " ".join(mixed_string), " ".join(replace_string)


class AsyncReader:
    def __init__(self, items):
        self.items = items

    def get_items(self):
        i = 1
        sentence_id = 0
        sentence_buffer = {}
        try:
            for sentence in self.items:
                sentence_id = sentence["id"]
                sentence_buffer[sentence_id] = sentence
    
                while i in sentence_buffer:
                    yield sentence_buffer[i]
                    del(sentence_buffer[i])
                    i+=1
        except:
            raise IndexError("Failure parsing file after entry with id: {}".format(sentence_id))
        

class WSDreader:
    def __init__(self, filename, filename_source=None, filename_tokenized=None, async=True):
        self.wsdfile = open(filename, 'rb')
        self.items = ijson.items(self.wsdfile, "documents.item")

        if async:
            self.items = AsyncReader(self.items).get_items()

        self.file_source = None
        self.file_tokenized = None

        if filename_source:
            self.file_source = open(filename_source)

        if filename_tokenized:
            self.file_tokenized = open(filename_tokenized)
    
    def __del__(self):
        self.wsdfile.close()

    def readlines(self):
        i = 0
        for sentence in self.items:
            i+=1
            if self.file_source:
                sentence_string = self.file_source.readline()
            else:
                sentence_string = sentence["string"]
    
            if self.file_tokenized:
                sentence_tokenized = self.file_tokenized.readline()
            else: 
                sentence_tokenized = sentence_string
    
            #it should further go with the tokenized version
            sentence_string = sentence_tokenized
            yield read_wsd_output(sentence, sentence_string)

from urllib import urlencode

class WSDclient:
    def __init__(self, url):
        self.url = url
        
    def annotate(self, text):
        text = urlencode(text)
        return urllib2.urlopen("{}/disambiguate?document={}&".format(self.url, text)).read()



import sys
if __name__ == "__main__":
   
    reader = WSDreader(sys.argv[1], sys.argv[2])
    writer1 = open(sys.argv[3], 'w')
    writer2 = open(sys.argv[4], 'w')
    
    for line1, line2 in reader.readlines():
        print >> writer1, line1
        print >> writer2, line2

    writer1.close()
    writer2.close()

            
            
            
                  
            
            
                
                
                
    
