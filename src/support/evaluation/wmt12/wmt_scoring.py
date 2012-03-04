'''
Created on 04 Mar 2012

@author: lefterav
'''
from sentence.dataset import DataSet
import os
import subprocess


class WmtScoring(DataSet):
    '''
    classdocs
    '''

    def process(self, reference_score_attribute_name, reference_rank_attribute_name, 
                score_attribute_name, rank_attribute_name, 
                method_name = "group_method", output_filename = "output.hyp", reference_filename = "reference.hyp",
                evaluation_script = None 
                ):
        
        if not evaluation_script:
            directory = os.path.dirname(__file__)
            evaluation_script = os.path.join(directory, "evaluateWMTQP2012.pl")
        
        self.create_files(reference_score_attribute_name, reference_rank_attribute_name, score_attribute_name, rank_attribute_name, method_name, output_filename, reference_filename)
        return self.run_command(evaluation_script,  reference_filename, output_filename)
        
    def create_files(self, reference_score_attribute_name, reference_rank_attribute_name, 
                score_attribute_name, rank_attribute_name, 
                method_name = "group_method", output_filename = "output.hyp", reference_filename = "reference.hyp"):
        output_file = open(output_filename, "w")
        reference_file = open(reference_filename, "w")
        i = 0
        for ps in self.parallelsentences:
            i+=1
            try:
                score_attribute_value = ps.get_attribute(score_attribute_name)
            except:
                score_attribute_value = "0"
            try:
                rank_attribute_value = ps.get_attribute(rank_attribute_name)
            except:
                rank_attribute_value = "0"
            output_file.write("{0}\t{1}\t{2}\t{3}\n".format(method_name, i, score_attribute_value, rank_attribute_value))
            
            try:
                reference_score_attribute_value = ps.get_attribute(reference_score_attribute_name)
            except:
                reference_score_attribute_value = "0"
            try:
                reference_rank_attribute_value = ps.get_attribute(reference_rank_attribute_name)
            except:
                reference_rank_attribute_value = "0"
            reference_file.write("{0}\t{1}\t{2}\t{3}\n".format("given_ref", i, reference_score_attribute_value, reference_rank_attribute_value))
            
    def run_command(self, evaluation_script, reference_filename, output_filename):
        process = subprocess.Popen(["perl", evaluation_script, reference_filename, output_filename], shell=False, stdout=subprocess.PIPE)
        score_string = process.communicate()[0]
        pattern =  "(\w*)\s*=[\[\s]*([\d*\-\.]*)"
        import re
        scores = dict(re.findall(pattern, score_string))
        os.remove(reference_filename)
        os.remove(output_filename)
        return scores
        
            