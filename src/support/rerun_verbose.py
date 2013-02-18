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
import sys

rounds = []
#####ROUND 2
#generic
#find . -wholename '*/steps/*wmt*decode.?'
r2_executions_generic = [("de-en", 8),
              ("en-de", 3),
              ("de-fr", 1),
              ("fr-de", 1),
              ("de-es", 3),
              ("es-de", 1),
              ]

#openoffice
#find . -wholename '*/steps/*openoffice3*decode.?'
r2_executions_technical = [("de-en", 8),
              ("de-es", 4),
              ("de-fr", 2),
              ("es-de", 3),
              ("fr-de", 2),
              ("en-de", 4),
              ]

r2_all_executions = r2_executions_generic
r2_all_executions.extend(r2_executions_technical)

r2_exclude_development = ["newstest2007", 
                       "newstest2009",                        
                       "openoffice-dev2011", 
                       "wmt11-reuse"]

r2_directory_pattern = "/share/taraxu/systems/r2/{}/moses/steps"

r2 = (r2_directory_pattern, r2_all_executions, r2_exclude_development, )
rounds.append(r2)


####ROUND 1
#find -L . -wholename '*/steps/*openoffice_*_decode.?'
#r1_executions_generic = [("de-en", 8),
#                         ("en-de", 6),
#                         ("es-de", 3), 
#                         ]
#
#r1_exclude_development = ["newstest2009.",
#                          "newstest2010.",
#                          "MultiUN"]
#
#r1_directory_pattern = "/share/taraxu/systems/generic2010/{}/steps"
#r1 = (r1_directory_pattern, r1_executions_generic, r1_exclude_development, )
#rounds.append(r1)





def _is_excluded(output_filename, exclude_development):
    for excluded_set in exclude_development:
        if excluded_set in output_filename:
            return True
    return False
         



if __name__ == '__main__':
    
    for directory_pattern, executions, exclude_development in rounds:
        for langpair, exp_id in executions:
            #comple the directory path where experiment is based
            directory = directory_pattern.format(langpair)
            filename_pattern = "*_decode.{}".format(exp_id)
            current_subdir = os.path.join(directory, str(exp_id))
            #print "subdir: ", current_subdir
            decoding_steps = fnmatch.filter(os.listdir(current_subdir), filename_pattern)
    #        print "decoding_steps", decoding_steps
            for decoding_step in decoding_steps:
                decoding_step_fullpath = os.path.join(current_subdir, decoding_step)
                decoding_commands = open(decoding_step_fullpath,'r').readlines()
                #print decoding_commands
                try:
                    moses_command = fnmatch.filter(decoding_commands,'*/moses *')
                    #print "matching commands found" , moses_command
                    moses_command = moses_command[0]
                except IndexError:
                    sys.stderr.write("Moses command for {}, {}, {} not found\n".format(current_subdir, exp_id, decoding_step))
                    continue
                    
    #            testset_name_pattern = "\/([^/]*).filtered"
                try:
                    basic_command , output_filename = moses_command.split(">")    
                except:
                    sys.stderr.write("Tried to split command \n\n{}\n\n Output file for {}, {}, {} not found\n".format(moses_command, current_subdir, exp_id, decoding_step))
                    continue
                
                #don't include this file if it contains the filename of a dev set (specified above)
                if _is_excluded(output_filename, exclude_development):
                    continue
                
                
                verbose_output_filename = output_filename.replace(".output.",".v2.output.").strip()
                verbose_log_filename = verbose_output_filename.replace(".v2.output.", ".v2.log.")
                basic_command = basic_command.replace("-threads 8", "")
                basic_command = basic_command.replace("-v 0", "-v 2")
                basic_command = basic_command.replace("/home/elav01/tools/moses/moses-cmd/src/moses", "/share/emplus/software/moses/moses-cmd/src/moses")
                
                #TODO: copy moses.ini and modify the lm settings to not use SRILM binarized for R1
    
                new_moses_command = "{} > {} 2> {}".format(basic_command, verbose_output_filename, verbose_log_filename)
                print new_moses_command
            
            
            
            
            
             
        
    