'''
Wraps around mGiza's trained models in order to perform force alignment of individual sentences
Development of this class has been halted due to bug of mGiza.

Created on Aug 2, 2014

@author: Eleftherios Avramidis
'''
import tempfile
import os
import subprocess
import re        

class GizaFeatureGenerator:
    """
    Class that wraps the mGiza trained models, so that individual sentences 
    can be aligned on demand 
    """
    
    def __init__(self, sourcelang, targetlang, gizadir, mosesdir, modeldir, tmpdir="/tmp"):
        '''
        @param gizadir: Full path of mGiza executable
        @type gizadir: str

        @param modeldir: Full path to model directory files
        @type modeldir: str
        '''
        self.gizadir = gizadir
        self.mosesdir = mosesdir
        self.modeldir = modeldir
        self.tmpdir = tmpdir
        
        self.sourcelang = sourcelang
        self.targetlang = targetlang
        
    
    def process_strings(self, source_string, target_string):
        #create temporary directory
        rundir = tempfile.mkdtemp(prefix="qtmp_", dir=self.tmpdir)
        os.chdir(rundir)
                
        #create temporary input parallel files with one sentence
        filestem = os.path.join(rundir, "sentence") 
        
        sourcefilename = "{}.{}".format(filestem, self.sourcelang)
        with open(sourcefilename, 'w') as sourcefile: 
            sourcefile.write(source_string)
        
        targetfilename = "{}.{}".format(filestem, self.targetlang)
        with open(targetfilename, 'w') as targetfile: 
            targetfile.write(source_string)
        
        #run script to temporary directory
        
        cmd_force_align = "export QMT_HOME={gizadir}; {gizadir}/scripts/force-align-moses-mod.sh {filestem} {sourcelang} {targetlang} {rundir}"
        cmd_merge_giza = "export QMT_HOME={gizadir}; {gizadir}/scripts/merge_alignment.py {rundir}/giza./{targetlang}-{sourcelang}.A3.final.part* > {rundir}/giza./{targetlang}-{sourcelang}.A3.final"
        cmd_merge_giza_inverse = "export QMT_HOME={gizadir}; {gizadir}/scripts/merge_alignment.py {rundir}/giza-inverse./{sourcelang}-{targetlang}.A3.final.part* > {rundir}/giza-inverse./{sourcelang}-{targetlang}.A3.final"
        cmd_symmetrize = '{mosesdir}/scripts/training/giza2bal.pl -d {rundir}/giza./{targetlang}-{sourcelang}.A3.final -i {rundir}/giza-inverse./{sourcelang}-{targetlang}.A3.final | {mosesdir}/bin/symal -alignment="grow" -diagonal="yes" -final="yes" -both="yes" > {rundir}/aligned.grow-diag-final-and'
        
        commands = [
                    cmd_force_align,
                    cmd_merge_giza,
                    cmd_merge_giza_inverse,
                    cmd_symmetrize
                    ]
        
        
        os.chdir(self.modeldir)
        for command in commands:
            command = command.format(
                                     gizadir = self.gizadir,
                                     mosesdir = self.mosesdir,
                                     filestem = filestem,
                                     sourcelang = self.sourcelang,
                                     targetlang = self.targetlang,
                                     rundir = rundir
                                     )
            print ">", command
            subprocess.check_call(command, shell=True)
        
           
        
        #delete temporary directory
        
        #return result
  
        

    def _convert_alingmentstring(self, string):
        pattern = "[^\s] \({\d*}\)"
    

if __name__ == "__main__":
    sourcestring = "das ist eine gute Idee , ich glaube"
    targetstring = "I think that this is a good idea"
    gfg = GizaFeatureGenerator(sourcelang = "de", 
                               targetlang = "en",
                               gizadir = "/project/qtleap/software/moses-2.1.1/mgizapp-code/mgizapp/",
                               mosesdir = "/project/qtleap/software/moses-2.1.1/mosesdecoder",
                               modeldir = "/local/tmp/elav01/selection-mechanism/systems/de-en/training",
                               tmpdir = "/local/tmp/elav01/selection-mechanism/systems/de-en/falign"
                               
                                 
    )
    gfg.process_strings(sourcestring, targetstring)    
