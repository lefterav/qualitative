'''
Created on 29 Aug 2012

@author: Eleftherios Avramidis
'''
import os
import subprocess
import re
import sys

class SvmRank(object):
    '''
    classdocs
    '''

    def __init__(self, directory="~/taraxu_tools/svm_rank"):
        '''
        Constructor
        '''
        self.directory = os.path.expanduser(directory)
        
    
    def learn(self, **kwargs):
        self.training_filename = kwargs.setdefault("training_filename", "/tmp/training.dat")
        self.model_filename = kwargs.setdefault("model_filename", "/tmp/model.dat")
        
        command = os.path.join(self.directory, "svm_rank_learn")
        commandline = [command]
        for argname, argvalue in kwargs.iteritems():
            if not argname in ["model_filename", "training_filename"]:
                commandline.append("-{}".format(argname))
                commandline.append("{}".format(argvalue))
        commandline.append(self.training_filename)
        commandline.append(self.model_filename)
        print " ".join(commandline)
        print subprocess.check_output(commandline)
    
    def classify(self, **kwargs):
#        self.training_filename = kwargs.setdefault("training_filename", "/tmp/training.dat")
#        self.model_filename = kwargs.setdefault("model_filename", "/tmp/model.dat")
        test_filename = kwargs.setdefault("test_filename", None)
        output_filename = kwargs.setdefault("output_filename", "/tmp/output.dat")
        
        command = os.path.join(self.directory, "svm_rank_classify")
        commandline = [command]
        for argname, argvalue in kwargs.iteritems():
            if not argname in ["test_filename", "output_filename"]:
                commandline.append("-{}".format(argname))
                commandline.append("{}".format(argvalue))
        commandline.append(test_filename)
        commandline.append(self.model_filename)
        commandline.append(output_filename)
        sys.stderr.write(" ".join(commandline))
        
        #run command
        output = subprocess.check_output(commandline)
        
        #process output to get statistics
        stats = self._stats_to_dict(output)
        return stats 
    
    def _stats_to_dict(self, string):
        """
        Extracts the basic statistics from the verbal response of SVMRank
        """
        stats = {}
        stats["runtime"] = float(re.findall("Runtime \(without IO\) in cpu-seconds: ([\d.]*)", string)[0])
        stats["error"], stats["correct"], stats["incorrect"], stats["total"] = re.findall("Zero/one-error on test set: ([\d.]*)% \((\d*) correct, (\d*) incorrect, (\d*) total\)", string)[0]
        stats["total_swapped"] = re.findall("Total Num Swappedpairs\s*:\s*(\d*)", string)[0]
        return stats