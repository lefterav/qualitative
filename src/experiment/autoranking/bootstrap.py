"""bootstrap.py
    module to set up a pipeline program
"""


import StringIO
from ConfigParser import ConfigParser
import classifier
import pkgutil
import orange

#from experiment.utils.ruffus_utils import (touch, sys_call,
#                                           main_logger as log,
#                                           main_mutex as log_mtx)

# --- config and options---
CONFIG_FILENAME = 'pipeline.cfg'
CONFIG_TEMPLATE = """
[general]
path = /home/elav01/taraxu_data/selection-mechanism/ml4hmt/experiment/109

[preprocessing]
pairwise = True
pairwise_exponential = True
allow_ties = False
generate_diff = False
merge_overlapping = True
orange_minimal = False

[training]
filename = /home/elav01/workspace/TaraXUscripts/data/multiclass/wmt08.if.jcml
class_name = rank
meta_attributes=id,testset
attributes = tgt-1_unk,tgt-2_unk,tgt-1_tri-prob,tgt-2_tri-prob,tgt-1_length_ratio,tgt-2_length_ratio,tgt-1_berkeley-n_ratio,tgt-2_berkeley-n_ratio,tgt-1_berkeley-n,tgt-2_berkeley-n,tgt-1_parse-VB,tgt-2_parse-VB,tgt-1_berkeley-loglikelihood_ratio,tgt-2_berkeley-loglikelihood_ratio,tgt-1_ibm1,tgt-2_ibm1
continuize=True
multinomialTreatment=NValues
continuousTreatment=NormalizeBySpan
classTreatment=Ignore

[testing]
filename = /home/elav01/taraxu_data/wmt-annotated/wmt10.ex.3.jcml
"""

# global configuration
cfg = ConfigParser()
cfg.readfp(StringIO.StringIO(CONFIG_TEMPLATE))  # set up defaults
cfg.read(CONFIG_FILENAME)  # add user-specified settings


def get_classifier(self, name):
    package = classifier
    prefix = package.__name__ + '.'
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        module = __import__(modname, fromlist="dummy")
        try:
            return getattr(module, name)
        except:
            pass
    return getattr(orange, name)

    
#
#def genome_path():
#    'returns the path to the genome fasta file (and downloads it if necessary)'
#    genome = worldbase(cfg.get('DEFAULT', 'worldbase_genome'), download=True)
#    return genome.filepath
#
#
#@files(None, genome_path())
#def get_genome(_, out_genome_path, touch_file=True):
#    'download the worldbase genome'
#    genome = worldbase(cfg.get('DEFAULT', 'worldbase_genome'), download=True)
#    if touch_file:
#        touch(out_genome_path)
#    return genome
#
#
#@files(None, '%s.chrom.sizes' % genome_path())
#def get_chrom_sizes(_, out_sizes):
#    'retrieve the chromosome sizes for the current genome from UCSC'
#    cmd = 'fetchChromSizes %s > %s' % (cfg.get('DEFAULT', 'genome'), out_sizes)
#    sys_call(cmd, file_log=False)
