from loonybin import Tool

class BuildStopwordList(Tool):
    def getName(self):
        return 'Machine Translation/Monolingual Corpus/Build Stopword List'
    
    def getDescription(self):
        return "Builds a stopword list by taking the n most frequent words from a pre-tokenized monolingual corpus"
    
    def getRequiredPaths(self):
        return []
    
    def getInputNames(self, params):
        return [ ('corpus', 'pre-tokenized monolingual corpus') ]

    def getParamNames(self):
        return [ ('numWords', 'number of most frequent words to include in the stopword list') ]

    def getOutputNames(self, params):
        return [ ('stopwords', 'Stopword list, one word per line') ]
    
    def getCommands(self, params, inputs, outputs):        
        return [ r"""cat %s \
| awk '{ for(i=1; i<=NF; i++) {
         cnt[$i]+=1
       }
     }
     END {
       for(tok in cnt) {
         print tok, cnt[tok]
     }}' \
     | sort -nrk2 | awk '{if(NR<=%s){print $1}}' \
     > %s
"""%(inputs['corpus'], params['numWords'], outputs['stopwords'])
       ]

    def getPostAnalyzers(self, params, inputs, outputs):
        return []

if __name__ == '__main__':
    import sys
    t = BuildStopwordList()
    t.handle(sys.argv)
