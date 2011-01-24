#!/usr/bin/env python
from libinstall import *

def installLoonyBinScripts(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/loonybin/scripts'%installDir
    writePathfile(pathsDir, pathName, path)
    
def installLoonyBinScripts(downloadedFile, installDir, pathName, pathsDir):
    path = '%s/loonybin/scripts'%installDir
    writePathfile(pathsDir, pathName, path)

#def installMeteor(downloadedFile, installDir, pathName, pathsDir):
#    run('sh %s'%downloadedFile)
#
#def installTER(downloadedFile, installDir, pathName, pathsDir):
#    extractTarball(downloadedFile, installDir)
#
#def installNIST(downloadedFile, installDir, pathName, pathsDir):
#    pass

def installScoring(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/scoring'%installDir
    writePathfile(pathsDir, pathName, path)

def installLmFilter(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/filter'%installDir
    writePathfile(pathsDir, pathName, path)

def installMoses(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    trunk = '%s/trunk'%installDir
    path = '%s/moses'%installDir
    run('rm -rf %s && mv %s %s'%(path, trunk, path))
    run('cd %s && (set -e; set -x; source ./regenerate-makefiles.sh) && ./configure && make'%path)
    writePathfile(pathsDir, pathName, path)

def installJoshua(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/joshua-1.2'%installDir
    writePathfile(pathsDir, pathName, path)

def installSAMT(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/SAMThadoop20100123'%installDir
    run('cd %s && mkdir O2 && cd O2 && ln -s ../dist/* . && ln -s ../src . && perl generatemakefile.pl > makefile && make'%path)
    writePathfile(pathsDir, pathName, path)
    
def installBerkeleyUnsupervisedAligner(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/berkeleyaligner'%installDir
    writePathfile(pathsDir, pathName, path)
    
def installBerkeleySupervisedAligner(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/berkeleyaligner'%installDir
    writePathfile(pathsDir, pathName, path)

def installMGIZA(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/mgizapp'%installDir
    run('cd %s && ./configure --prefix=%s && make && make install'%(path, installDir))
    writePathfile(pathsDir, pathName, path)

def installChaksi(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/Chaski'%installDir
    #run('cd %s/Chaksi && ant'%(installDir))
    writePathfile(pathsDir, pathName, path)    
    
def installStanfordEnglishParser(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/stanford-parser'%installDir
    writePathfile(pathsDir, pathName, path)

def installLinguaAlignmentToolkit(downloadedFile, installDir, pathName, pathsDir):
    extractTarball(downloadedFile, installDir)
    path = '%s/Lingua-AlignmentSet-1.1'%installDir
    writePathfile(pathsDir, pathName, path)

deps = [
#    ('meteor','Meteor Evaluation Metric V1.0','http://www.cs.cmu.edu/~alavie/METEOR/install-meteor-1.0.sh', installMeteor),
#    ('tercom','TER Evaluation Metric V0.7.25', 'http://www.cs.umd.edu/~snover/tercom/tercom-0.7.25.tgz', installTER),
#    ('nist-bleu','NIST BLEU Evaluation Metric V13a','ftp://jaguar.ncsl.nist.gov/mt/resources/mteval-v13a.pl', installNIST),
    ('multimetric','MultiMetric Scoring Script for BLEU/NIST/TER/METEOR','http://kheafield.com/code/scoring.tar.gz', installScoring),
    ('lm-filter','Test Set Filter for ARPA Language Models','http://kheafield.com/code/filter.tar.gz',installLmFilter),
    ('moses','Moses Factored PBSMT Decoder','http://iweb.dl.sourceforge.net/project/mosesdecoder/mosesdecoder/2009-04-13/moses-2009-04-13.tgz', installMoses),
    ('joshua','Joshua Chart-based Decoder','http://downloads.sourceforge.net/project/joshua/joshua/1.2/joshua-1.2.tgz?use_mirror=kent', installJoshua),
    ('samt','SAMT Chart-based Decoder','http://www.cs.cmu.edu/~zollmann/samt/SAMThadoop20100123.tgz', installSAMT),
    ('berkeley-unsupervised-aligner','Berkeley Unsupervised Discriminative Word Aligner','http://berkeleyaligner.googlecode.com/files/berkeleyaligner_unsupervised-2.1.tar.gz', installBerkeleyUnsupervisedAligner),
    ('berkeley-supervised-aligner','Berkeley Supervised Discriminative Word Aligner','http://berkeleyaligner.googlecode.com/files/berkeleyaligner-2.0.tar.gz', installBerkeleySupervisedAligner),
    ('mgiza','MGIZA++ Multi-Threaded Word Alignment','http://downloads.sourceforge.net/project/mgizapp/mgizapp-0.6.3.tar.gz?use_mirror=kent', installMGIZA),
    ('chaksi','Chaksi Distributed Word Alignment and Phrase Extraction','http://downloads.sourceforge.net/project/chaski/chaski/chaski-0.2.4.tar.gz?use_mirror=kent', installChaksi),
#    ('stanford-en-parser','Stanford English Parser', 'http://nlp.stanford.edu/software/stanford-parser-2008-10-26.tgz', installStanfordEnglishParser), # included with SAMT
    ('lingua-alignment-toolkit','Lingua Alignment Toolkit V1.1 for AER Evaluation', 'http://gps-tsc.upc.es/veu/personal/lambert/software/Lingua-AlignmentSet-1.1.tgz', installLinguaAlignmentToolkit)
    ]

runInstaller(deps)
