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

    def process(self, reference_score_attribute_name, 
                score_attribute_name, 
                mode = "rank",
                method_name = "group_method", output_filename = "output.hyp", reference_filename = "reference.hyp",
                evaluation_script = None, 
                ):
        
        if not evaluation_script:
            directory = os.path.dirname(__file__)
            evaluation_script = os.path.join(directory, "evaluateWMTQP2012.pl")
        
        self.create_files(reference_score_attribute_name, score_attribute_name, method_name, output_filename, reference_filename, mode)
        return self.run_command(evaluation_script,  reference_filename, output_filename)
        
    def create_files(self, reference_score_attribute_name, 
                score_attribute_name, 
                method_name = "group_method", output_filename = "output.hyp", reference_filename = "reference.hyp", mode = "rank"):
        output_file = open(output_filename, "w")
        reference_file = open(reference_filename, "w")
        i = 0
        for ps in self.parallelsentences:
            i+=1

            if mode == "score":
                score_attribute_value = ps.get_attribute(score_attribute_name)
                try:
                    reference_score_attribute_value = ps.get_attribute(reference_score_attribute_name)
                except:
                    reference_score_attribute_value = ps.get_translations()[0].get_attribute(reference_score_attribute_name)
                rank_attribute_value = "-1000"
                reference_rank_attribute_value = "-1"
            elif mode == "rank":
                reference_rank_attribute_value = ps.get_attribute(reference_score_attribute_name)
                rank_attribute_value = ps.get_attribute(score_attribute_name)
                score_attribute_value = "-1000"
                reference_score_attribute_value = "-1"
            
            output_file.write("{0}\t{1}\t{2}\t{3}\n".format(method_name, i, score_attribute_value, rank_attribute_value))
            
            reference_file.write("{0}\t{1}\t{2}\t{3}\n".format("given_ref", i, reference_score_attribute_value, reference_rank_attribute_value))
            
    def run_command(self, evaluation_script, reference_filename, output_filename):
        process = subprocess.Popen(["perl", evaluation_script, reference_filename, output_filename], shell=False, stdout=subprocess.PIPE)
        score_string = process.communicate()[0]
        pattern =  "(\w*)\s*=[\[\s]*([\d*\-\.]*)"
        import re
        scores = dict(re.findall(pattern, score_string))
        try:
            scores["interval1"], scores["interval2"] = str(scores["Interval"]).split('-')
            del(scores["Interval"]) 
        except:
            pass
#        os.remove(reference_filename)
#        os.remove(output_filename)
        return scores

if __name__ == '__main__':
    import sys
    import os
    from io_utils.input.jcmlreader import JcmlReader
    classified_jcml = sys.argv[1]
    mode = sys.argv[2]
    reference_score_attribute_name = sys.argv[3]
    score_attribute_name = sys.argv[4]
    
    classified_dataset = JcmlReader(classified_jcml).get_dataset()
    ret = WmtScoring(classified_dataset).process(reference_score_attribute_name, score_attribute_name, "score")
    clean_str = " ".join(["{0}:{1}".format(k,v) for k,v in ret.iteritems()])
    if sys.argv[5] == "--fix-output":
        current_path = os.path.dirname(classified_jcml)
        output_filename = os.path.join(current_path, '0.log')
        output_file = open(output_filename, 'a')
        output_file.write("{0}\n".format(clean_str))
        output_file.close()
        