'''
Created on 23 Feb 2012

@author: lefterav
'''
from itertools import combinations
import sys
from dataset import DataSet
from coupledparallelsentence import CoupledParallelSentence
from io.input.orangereader import OrangeData

class CoupledDataSet(DataSet):
    '''
    A coupled data set contains all possible couples of parallel sentences of a simple dataset
    @ivar parallelsentences: a list of the coupled parallel sentences
    @type parallelsentences: [L{CoupledParallelSentence}, ...]
    '''


    def __init__(self, existing_item):
        '''
        @var existing_item: allows the construction of a coupled dataset from an existing simple dataset or already coupled parallel sentences
        @type existing_item: L{DataSet} or [L{CoupledParallelSentence}, ...]
        '''
        self.parallelsentences = []
        self.attribute_names_found = False
        self.attribute_names = []
        
        if isinstance(existing_item, DataSet):
            dataset = existing_item
            parallelsentences = dataset.get_parallelsentences()
            ps_combinations = combinations(parallelsentences, 2)
            self.parallelsentences = [CoupledParallelSentence(ps1, ps2) for ps1, ps2 in ps_combinations]
            
            
    def get_single_set(self, critical_attribute="predicted_rank"):
        '''
        Reconstructs the original data set, with only one sentence per entry.
        @return: Simple dataset that contains the simplified parallel sentences
        @rtype: L{DataSet}
        '''
        single_parallelsentences = {}
        for coupled_parallelsentence in self.parallelsentences:
            ps1, ps2 = coupled_parallelsentence.get_couple()
            single_parallelsentences[ps1.get_tuple_id()] = ps1
            single_parallelsentences[ps2.get_tuple_id()] = ps2
        
        sorted_keys = sorted(single_parallelsentences)
        sorted_ps = [single_parallelsentences[key] for key in sorted_keys]
        return DataSet(sorted_ps)
    
    
    def get_single_set_with_hard_ranks(self, critical_attribute="predicted_rank"):
        '''
        Reconstructs the original data set, with only one sentence per entry.
        @return: Simple dataset that contains the simplified parallel sentences
        @rtype: L{DataSet}
        '''
        single_parallelsentences = {}
        single_parallelsentences_rank = {}
        for coupled_parallelsentence in self.parallelsentences:
            ps1, ps2 = coupled_parallelsentence.get_couple()
            rank = int(coupled_parallelsentence.get_attribute(critical_attribute))
             
            int(ps2.attributes["predicted_rank"]) - rank
            single_parallelsentences[ps1.get_tuple_id()] = ps1
            try:
                single_parallelsentences_rank[ps1.get_tuple_id()] += rank
            except:
                single_parallelsentences_rank[ps1.get_tuple_id()] = rank
            
            single_parallelsentences[ps2.get_tuple_id()] = ps2
            try:
                single_parallelsentences_rank[ps2.get_tuple_id()] -= rank
            except:
                single_parallelsentences_rank[ps2.get_tuple_id()] = -1 * rank
            
        
        sorted_keys = sorted(single_parallelsentences)
        sorted_ps = []
        for key in sorted_keys:
            ps = single_parallelsentences[key]
            ps.add_attributes({critical_attribute: single_parallelsentences_rank[key]})
            sorted_ps.append(ps)
        return DataSet(sorted_ps)
    
    def get_nested_attribute_names(self):
        return []
        
                    

class OrangeCoupledDataSet(OrangeData):
    """
    A wrapper for the orange Example Table that can be initialized upon a CoupledDataSet
    @todo: maybe change that to a function of the previous class and break down to the parallel sentences
    """
    
    def _get_orange_header(self, dataset, class_name, attribute_names, desired_attributes=[], meta_attributes=[]):

        #first construct the lines for the declaration
        line_1 = "" #line for the name of the arguments
        line_2 = "" #line for the type of the arguments
        line_3 = "" #line for the definition of the class 
        print "Getting attributes"
        
        if desired_attributes == []:
            desired_attributes = attribute_names
        
        
        #if no desired attribute define, get all of them
        #if not desired_attributes:
        #    desired_attributes =  attribute_names
        
        print "Constructing file"
        #prepare heading
        for attribute_name in attribute_names :
            #line 1 holds just the names
            attribute_name = str(attribute_name)
            line_1 += attribute_name +"\t"
            
            #TODO: find a way to define continuous and discrete arg
            #line 2 holds the class type
            if attribute_name == class_name:
                line_2 += "discrete\t"
            elif attribute_name in desired_attributes and attribute_name not in meta_attributes:
                line_2 += "continuous\t"
            else:
                line_2 += "string\t"

            
            #line 3 defines the class and the metadata
            if attribute_name == class_name:
                line_3 = line_3 + "c"
            elif attribute_name not in desired_attributes or attribute_name in meta_attributes:
                #print attribute_name , "= meta"
                line_3 = line_3 + "m"
            line_3 = line_3 + "\t"
        
        #if not self.avoidstrings:
        #src
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "src-1\t"
        
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "src-2\t"
        #target
        i=0
        for tgt in dataset.get_parallelsentences()[0].get_translations():
            i+=1
            line_2 += "string\t"
            line_3 += "m\t"
            line_1 += "tgt-" + str(i) + "\t"
        #ref 
        line_2 += "string\t"
        line_3 += "m\t"
        line_1 += "ref\t"
    
        #break the line in the end
        line_1 = line_1 + "\n"
        line_2 = line_2 + "\n"
        line_3 = line_3 + "\n"
        output = line_1 + line_2 + line_3
        return output
    
    
    def _getOrangeFormat(self, orange_file, dataset, class_name, desired_attributes=[], meta_attributes=[]):
        sys.stderr.write("retrieving attribute names\n")
        attribute_names = dataset.get_all_attribute_names()

        sys.stderr.write("processing orange header\n") 
        output = self._get_orange_header(dataset, class_name, attribute_names, desired_attributes, meta_attributes)
        sys.stderr.write("processing content\n")
        
        orange_file.write(output)
 
        for psentence in dataset.get_parallelsentences():
            outputlines = []
            #sys.stderr.write("getting nested attributes\n")
            nested_attributes = psentence.get_nested_attributes()
            if nested_attributes == {}:
                nested_attributes = psentence.get_attributes()
            
            nested_attribute_names = nested_attributes.keys()
            
            #sys.stderr.write("printing content\n")
            for attribute_name in attribute_names:
                if attribute_name in nested_attribute_names:
                    outputlines.append(nested_attributes[attribute_name])
                    
                #even if attribute value exists or not, we have to tab    
                outputlines.append ("\t")
                
            #if not self.avoidstrings:
            outputlines.append( psentence.get_source()[0].get_string())
            outputlines.append("\t")
            
            outputlines.append( psentence.get_source()[1].get_string())
            outputlines.append("\t")
            
            for tgt in psentence.get_translations():
                outputlines.append(tgt.get_string())
                outputlines.append("\t")
            try:
                outputlines.append(psentence.get_reference().get_string())
                outputlines.append("\t")
            except:
                outputlines.append("\t")
            outputlines.append("\n")
            orange_file.writelines(outputlines)
                
                