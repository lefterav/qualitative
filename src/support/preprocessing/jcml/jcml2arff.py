'''
Created on 06 Mar 2012

@author: lefterav
'''
from lxml import etree
from io_utils.input.jcmlreader import JcmlReader

class ArffWriter:
    def __init__(self, output_filename, class_type, class_values=[], numeric_attribute_names=[], string_attribute_names=[], nominal_attributes={}):
        self.f = open(output_filename, 'w')
        self.class_type = class_type
        self.class_values = class_values
        self.numeric_attribute_names = numeric_attribute_names
        self.string_attribute_names = string_attribute_names
        self.nominal_attributes = nominal_attributes

    def write_header(self, relation_name, ):
        self.f.write("@RELATION {0}\n\n".format(relation_name))
        
        for attribute_name in self.numeric_attribute_names:
            self.f.write("@ATTRIBUTE {0}\tNUMERIC\n".format(attribute_name))
        for attribute_name in self.string_attribute_names:
            self.f.write("@ATTRIBUTE {0}\tSTRING\n".format(attribute_name))
        for attribute_name, values in self.nominal_attributes.iteritems():
            self.f.write("@ATTRIBUTE %s\t{%s}\n" % (attribute_name, ",".join(values)))

        if self.class_type == "numeric":
            self.f.write("@ATTRIBUTE class\tNUMERIC\n")
        elif self.class_type == "nominal":
            self.f.write("@ATTRIBUTE class\t{%s}\n\n" % (",".join(self.class_values)))
        self.f.write("@DATA\n")
    
    def write_instance(self, attributes ={}, class_value = ""):
        
        for attribute_name in self.numeric_attribute_names:
            try:
                self.f.write("{0},".format(attributes[attribute_name].replace("inf", "999999").replace("nan", "0")))
            except KeyError:
                self.f.write("0,")
        for attribute_name in self.string_attribute_names:
            try:
                self.f.write("{0},".format(attributes[attribute_name].replace("nan", "0")))
            except KeyError:
                self.f.write("0,")
        for attribute_name, values in self.nominal_attributes.iteritems():
            try:
                self.f.write("{0},".format(attributes[attribute_name].replace("nan", "0")))
            except KeyError:    
                self.f.write("{0},".format(list(values)[0]))
        self.f.write("{0}\n".format(class_value))

    def close(self):
        if self.f:
            self.f.close()
    def __del__(self):
        self.close()

class Jcml2Arff:
    def process(self, jcml_filename, arff_filename, 
                hidden_attribute_names, discrete_attribute_names, string_attribute_names, 
                relation_name, class_name, class_type, class_values):
        dataset = JcmlReader(jcml_filename).get_dataset()
        attribute_names = set(dataset.get_all_attribute_names()) - set(hidden_attribute_names)
        nominal_attributes = dataset.get_discrete_attribute_values(discrete_attribute_names)
        numeric_attribute_names = attribute_names - set(discrete_attribute_names)
        arff = ArffWriter(arff_filename, class_type, class_values, numeric_attribute_names, string_attribute_names, nominal_attributes)
        arff.write_header(relation_name)
        
        for ps in dataset.get_parallelsentences():

            atts = {}
            atts.update(ps.attributes)
            atts.update(ps.get_nested_attributes())
            class_value = atts[class_name]
            del(atts[class_name])
            for attname in hidden_attribute_names:
                try:
                    del(atts[attname])
                    print "deleted", attname 
                except:
                    pass
            arff.write_instance(atts, class_value)
        arff.close()


if __name__ == '__main__':
    hidden_attributes = ["tgt-1_berkeley-tree", "src_berkeley-tree","ref_berkeley-tree",                         
                         "testset", "judgment-id", "langsrc", "langtgt", "ps1_judgement_id", 
                               "id", "tgt-1_score" ,  "tgt-1_system" ,    
                                 ]
    discrete_attributes = [ "src_reuse_status",  
                       "src_terminologyAdmitted_status", 
                       "src_total_status", 
                       "src_spelling_status",  
                       "src_style_status",  
                       "src_grammar_status",  
                       "src_terminology_status",
                       "src_resultStats_projectStatus", 
                       ]
    Jcml2Arff().process("/home/lefterav/taraxu_data/wmt12/qe/training_set/training.all.analyzed.f.jcml", 
                        "/home/lefterav/taraxu_data/wmt12/qe/training_set/trainset.arff", 
                        hidden_attributes, discrete_attributes, [], "qe", "tgt-1_score", "numeric", [])