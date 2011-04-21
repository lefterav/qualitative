"""
@author: Eleftherios Avramidis
"""

from sentence.dataset import DataSet
import codecs

class Wmt11TabWriter(object):
    """
    classdocs
    """
    

    def __init__(self, data, name="dfki", testset="testset"):
        """
        Constructor
        """
        self.metric_name = name
        self.testset = testset
        
        if isinstance(data, list):
            self.object_xml = None
            self.convert_to_tab(data)
        elif isinstance(data, DataSet):
            self.object_xml = None
            self.convert_to_tab(data.get_parallelsentences())
        
    def convert_to_tab(self, parallelsentences):
        """
        Creates an tab for the document an populates that with the (parallel) sentences of the given object.
        Resulting tab string gets stored as a variable.
        @param parallelsentences: a list of ParallelSentence objects 
        """
        
        entries = []
        entries.append("<METRIC NAME>\t<LANG-PAIR>\t<TEST SET>\t<SYSTEM>\t<SEGMENT NUMBER>\t<SEGMENT SCORE>")
                
        for ps in parallelsentences:
            ps_att = ps.get_attributes()
            if ps_att.get("testset"):
                testset = ps_att["testset"]
            else:
                testset = self.testset
            for tgt in ps.get_translations():
                t_att = tgt.get_attributes()                
                entry = "\t".join([self.metric_name, "%s-%s" % (ps_att["langsrc"], ps_att["langtgt"]), testset, t_att["system"], ps_att["id"], t_att["rank"]])
                entries.append(entry)  
            
        #entries = sorted (entries, key=lambda entry: entry.split("\t")[4])
        self.content =  "\n".join(entries)
        
    def write_to_file(self, filename):
        file_object = codecs.open(filename, 'w', 'utf-8')
        file_object.write(self.content)
        file_object.close()  
           