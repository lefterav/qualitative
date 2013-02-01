'''
Rerun a series of Moses experiments, with verbose output
Dig into a list of given Moses EMS executions for particular experiments
and repeat them with modified verbose settings towards new output files  

Created on 1 Feb 2013

@author: elav01
'''

import os
import fnmatch
import re

executions = [("/share/taraxu/systems/r2/en-de", 1)]


if __name__ == '__main__':
    for dir, round in executions:
        filename_pattern = "*_decode.{}*".format(round)
        decoding_steps = fnmatch.filter(os.listdir(dir), filename_pattern)
        for decoding_step in decoding_steps:
            decoding_commands = open(decoding_step,'r').readlines()
            try:
                moses_command = fnmatch.filter('*bin/moses*')[0]
            except IndexError:
                print "Moses command for {}, {}, {} not found".format(dir, round, decoding_step)
                continue
                
            output_file_pattern = "> (.*)"
#            testset_name_pattern = "\/([^/]*).filtered"
            try:
                output_filename = re.findall(output_file_pattern, moses_command)[0]
                
            except IndexError:
                print "Moses command for {}, {}, {} not found".format(dir, round, decoding_step)
            
            verbose_output_filename = output_filename.replace(".output.",".v2.output.")
            verbose_log_filename = verbose_output_filename.replace(".v2.output.", ".v2.output.log.")
            
            new_moses_command = moses_command.sub()
            
            
            
            
            
             
        
    