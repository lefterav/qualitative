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
    for directory, exp_id in executions:
        filename_pattern = "*_decode.{}*".format(exp_id)
        decoding_steps = fnmatch.filter(os.listdir(directory), filename_pattern)
        for decoding_step in decoding_steps:
            decoding_commands = open(decoding_step,'r').readlines()
            try:
                moses_command = fnmatch.filter('*bin/moses*')[0]
            except IndexError:
                print "Moses command for {}, {}, {} not found".format(directory, round, decoding_step)
                continue
                
#            testset_name_pattern = "\/([^/]*).filtered"
            try:
                basic_command , output_filename = moses_command.split(",")
                
                
            except:
                print "Moses command for {}, {}, {} not found".format(directory, round, decoding_step)
                continue
            
            verbose_output_filename = output_filename.replace(".output.",".v2.output.")
            verbose_log_filename = verbose_output_filename.replace(".v2.output.", ".v2.output.log.")
            
            new_moses_command = "{} > {} 2> {}".format(basic_command, verbose_output_filename, verbose_log_filename)
            print new_moses_command
            
            
            
            
            
             
        
    