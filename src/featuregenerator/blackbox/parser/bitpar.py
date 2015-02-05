#!/usr/bin/python
#from __future__ import print_function	

""" 
Code from https://github.com/andreasvc/eodop/blob/master/bitpar.py

Shell interface to bitpar, an efficient chart parser for (P)CFGs.
Expects bitpar to be compiled and available in the PATH.
Currently only yields the one best parse tree without its probability.
Todo: 
 - yield n best parses with probabilites (parameter)
 - parse chart output"""

from pexpect import spawn
from time import sleep
import os, re
import logging as log
from featuregenerator.languagefeaturegenerator import LanguageFeatureGenerator
from collections import OrderedDict
from numpy import average, std
from featuregenerator.preprocessor import CommandlinePreprocessor
from xml.etree import cElementTree
from dataprocessor.sax.saxps2jcml import IncrementalJcml
from dataprocessor.ce.cejcml import CEJcmlReader
from tempfile import mkstemp
import codecs

from subprocess import check_call

class BitPar(CommandlinePreprocessor, LanguageFeatureGenerator):
	def __init__(self, path,
				lexicon_filename,
				grammar_filename,
				unknownwords,
				openclassdfsa, 
				language,
				timeout=30,
				rootsymbol='TOP',
				n=100):
		path = os.path.join(path, "bitpar")
		command_template = "{path} -q -b {n} -vp -s {rootsymbol} -u {unknownwords} -w {openclassdfsa} {grammar} {lexicon}".format(path=path,
																																n=n,
																																rootsymbol=rootsymbol,
																																unknownwords=unknownwords,
																																openclassdfsa=openclassdfsa,
																																grammar=grammar_filename,
																																lexicon=lexicon_filename
																																)
		super(BitPar, self).__init__(path, language, {}, command_template)
	
		
	def get_features_string(self, string):
		att = OrderedDict()
		try: 
			parses = self.nbest_parse(string)
		except:
			parses = []
			
		if not parses:
			return {'bit_failed': 1}
		att['bit_failed'] = 0
		best_parse = sorted(parses)[0]
		att["bit_tree"], att["bit_prob"] = best_parse
		att["bit_n"] = len(parses)
		probabilities = [prob for _, prob in parses]
		att["bit_avgprob"] = average(probabilities)
		att["bit_stdprob"] = std(probabilities)
		att["bit_minprob"] = min(probabilities)
		if att["bit_prob"] > (att["bit_avgprob"] + att["bit_stdprob"]):
			att["bit_probhigh"] = 1
		else:
			att["bit_probhigh"] = 0
		return att
		
	def nbest_parse(self, sent):
		""" n has to be specified in the constructor because it is specified
		as a command line parameter to bitpar, allowing it here would require
		potentially expensive restarts of bitpar. """
		
		if self.bitpar.terminated: self.start()
		log.debug("BitParChartParser: sending sentence '{}'".format(sent))
		sent = "\n".join(sent.strip().split()) + "\n\n"
		output = self.process_string(sent)
		log.debug("BitParChartParser: received sentence '{}'".format(sent.replace("\n", " ")))
		# remove bitpar's escaping (why does it do that?), strip trailing blank line
		results = re.sub(r"\\([/{}\[\]<>'\$])", r"\1", output).splitlines()[:-1]
		
		probs = [float(a.split("=")[1]) for a in results[::2] if "=" in a]
		trees = [a for a in results[1::2]]
		return zip(trees, probs)
	

class BitParChartParser:
	def __init__(self, lexicon_filename=None, grammar_filename=None, rootsymbol="TOP", unknownwords=None, openclassdfsa=None, cleanup=True, n=3, path=None, timeout=10):
		""" Interface to bitpar chart parser. Expects a list of weighted
		productions with frequencies (not probabilities).
		
		@param rootsymbol: starting symbol for the grammar
		@param unknownwords: a file with a list of open class POS tags 
			with frequencies
		@param openclassdfsa: a deterministic finite state automaton,
			refer to the bitpar manpage.
		@param cleanup: boolean, when set to true the grammar files will be
			removed when the BitParChartParser object is deleted.
		@param name: filename of grammar files in case you want to export it,
			if not given will default to a unique identifier
		@param n: the n best parse trees will be requested
			"""

		self.grammar_filename = grammar_filename
		self.lexicon_filename = lexicon_filename
		self.path = path
		log.debug("BitParChartParser path: {}".format(path))
		self.rootsymbol = rootsymbol
		self.timeout = timeout
		self.cleanup = cleanup
		self.n = n
		self.unknownwords = unknownwords
		self.openclassdfsa = openclassdfsa
		self.start()


	def start(self):
		# quiet, yield best parse, show viterbi prob., use frequencies
		if self.path:
			executable = os.path.join(self.path, 'bitpar')
		else:
			executable = 'bitpar'
		self.cmd = "%s -q -b %d -vp " % (executable, self.n)
		if self.rootsymbol: 
			self.cmd += "-s %s " % self.rootsymbol
		if self.unknownwords: 
			self.cmd += "-u %s " % self.unknownwords
		if self.openclassdfsa: 
			self.cmd += "-w %s " % self.openclassdfsa
		if self.lexicon_filename and self.grammar_filename:
			self.cmd += " %s %s" % (self.grammar_filename, self.lexicon_filename)
		log.debug("BitParChartParser command: {}".format(self.cmd))
		self.bitpar = spawn(self.cmd)
		self.bitpar.setecho(False)
		# allow bitpar to initialize; just to be sure
		sleep(1)
		try: 
			self.bitpar.read_nonblocking(size=1024, timeout=0)
		except: 
			pass
	def stop(self):
		if not self.bitpar.terminated: self.bitpar.terminate()

	def parse(self, sent):
		return sorted(self.nbest_parse(sent))[0] 

	def nbest_parse(self, sent):
		""" n has to be specified in the constructor because it is specified
		as a command line parameter to bitpar, allowing it here would require
		potentially expensive restarts of bitpar. """
		
		if self.bitpar.terminated: self.start()
		log.debug("BitParChartParser: sending sentence '{}'".format(sent))
		sent = "\n".join(sent.strip().split()) + "\n\n\n\n"
		self.bitpar.send(sent)
		log.debug("BitParChartParser: sent '{}'".format(sent.strip().replace("\n"," ")))
		output = []
		while not output.endswith("\r\n\r\n"):
			try:
				chars = self.bitpar.read_nonblocking(size=32767, timeout=self.timeout)
				log.debug("Characters: {}".format(chars))
				output.append(chars)
			except:
			    log.warning("BitParChartParser: exception caused by sentence '{}'".format(sent.strip().replace("\n", " ")))
			    break
			sleep(1)
			log.debug("Waiting one more second")
		output = "".join(output)
		log.debug("BitParChartParser: received sentence '{}'".format(sent.replace("\n", " ")))
		# remove bitpar's escaping (why does it do that?), strip trailing blank line
		results = re.sub(r"\\([/{}\[\]<>'\$])", r"\1", output).splitlines()[:-1]
		
		probs = [float(a.split("=")[1]) for a in results[::2] if "=" in a]
		trees = [a for a in results[1::2]]
		return zip(trees, probs)
		
		
		
	#===========================================================================
	# def batch_parse(self, sents, n=1):
	# 	"""Batch parse a series of sentences. Expects a lists of
	# 	sentences in the form of lists of words.  Returns a list of lists, each being
	# 	up to n resulting trees.
	# 	Caveat: if you haven't supplied an unknown words file, bitpar
	# 	will stop parsing after the first unknown word; if a sentence cannot
	# 	be parsed for another reason, bitpar will continue. """
	# 	f = "/tmp/%s" % uuid1()
	# 	open(f, "w").writelines("%s\n\n" % "\n".join(sent) for sent in sents)
	# 	bitpar = Popen((self.cmd + " " + f).split(), stdout=PIPE, stderr=PIPE)
	# 	output = bitpar.stdout.read()
	# 	output = re.sub(r"\\([/{}\[\]<>'\$])", r"\1", output).split("\n\n")[:-1]
	# 	result = []
	# 	for a in output:
	# 		results = a.splitlines()
	# 		if "No parse" in results[0]:
	# 			result.append(( (), () ))
	# 			continue
	# 		probs = (float(a.split("=")[1]) for a in results[::2] if "=" in a)
	# 		trees = (Tree(a) for a in results[1::2])
	# 		result.append((probs, trees))
	# 	Popen(("rm %s" % f).split())
	# 	return ([ProbabilisticTree(b.node, b, prob=a) for a, b in zip(probs, trees)] for probs, trees in result)
	# 	
	
class BitParserFeatureGenerator(LanguageFeatureGenerator):
	def __init__(self, path,
				lexicon_filename,
				grammar_filename,
				unknownwords,
				openclassdfsa, 
				language,
				timeout=30,
				n=100):
		log.debug("BitParserFeatureGenerator path: {}".format(path))
		self.lang = language
		self.parser = BitParChartParser(lexicon_filename=lexicon_filename, 
		        grammar_filename=grammar_filename, 
		        unknownwords=unknownwords, 
		        openclassdfsa=openclassdfsa, 
		        n=n, 
		        path=path, 
		        timeout=timeout)
	
	def get_features_string(self, string):
		 
		try: 
			parses = self.parser.nbest_parse(string)
		except:
			parses = []
			
		if not parses:
			return {'bit_failed': 1}
		else:
			return get_bitpar_features(parses)
		





class BatchProcessor:


	def process_source_batch(self, input_filename, output_filename):
		input_textfilename = self._source_batch_to_textfile(input_filename)
		_, output_textfilename = mkstemp(suffix=".src.bit", prefix="tmp_bitpar_", dir=self.tmpdir)
		
		log.error(" ".join(self.command))
		log.error(input_textfilename)
		log.error(output_textfilename)
		
		check_call(self.command, 
				stdin=open(input_textfilename), 
				stdout=open(output_textfilename, 'w'))

		features = self.get_features_batch(output_textfilename)
		self._add_features_to_source_batch(input_filename, output_filename, features)
		
	def _source_batch_to_textfile(self, input_filename):
		_, input_textfilename = mkstemp(suffix=".src.txt", prefix="tmp_bitpar_", dir=self.tmpdir)
		input_textfile = codecs.open(input_textfilename, 'w', 'utf-8')		
		
		input_batch = self.reader(input_filename)
		for parallelsentence in input_batch.get_parallelsentences():
			#print (parallelsentence.get_source().get_string(), file=input_textfile)
			converted_line = u"\n".join(parallelsentence.get_source().get_string().strip().split())
			input_textfile.write(u"{}\n\n\n".format(converted_line))
		input_textfile.close()
		return input_textfilename
	
	def _add_features_to_source_batch(self, input_filename, output_filename, features=[]):
		input_batch = self.reader(input_filename)
		output_batch = self.writer(output_filename)
		i = 0
		for parallelsentence in input_batch.get_parallelsentences():
			sentence_features = features.next()
			parallelsentence.source.att.update(sentence_features)
			i+=1
			output_batch.add_parallelsentence(parallelsentence)		
		output_batch.close()
			

	def process_target_batch(self, input_filename, output_filename):
		input_textfilename = self._target_batch_to_textfile(input_filename)
		_, output_textfilename = mkstemp(suffix=".tgt.bit", prefix="tmp_bitpar_", dir=self.tmpdir)
				
		check_call(self.command, 
				stdin=open(input_textfilename), 
				stdout=open(output_textfilename, 'w'))

		features = self.get_features_batch(output_textfilename)
		self._add_features_to_target_batch(input_filename, output_filename, features)
				
	def _target_batch_to_textfile(self, input_filename):
		_, input_textfilename = mkstemp(".tgt.txt", "tmp_bitpar_", dir=self.tmpdir)
		input_textfile = codecs.open(input_textfilename, 'w')		
		
		input_batch = self.reader(input_filename)
		for parallelsentence in input_batch.get_parallelsentences():
			for target in parallelsentence.get_translations():
				print >> input_textfile, target.get_string()
				#print(target.get_string(), file=input_textfile)
		input_textfile.close()
		return input_textfilename
	
	def _add_features_to_target_batch(self, input_filename, output_filename, features=[]):
		input_batch = self.reader(input_filename)
		output_batch = self.writer(output_filename)
		i = 0
		for parallelsentence in input_batch.get_parallelsentences():
			for target in parallelsentence.tgt:
				sentence_features = next()
				target.att.update(sentence_features)
				i+=1
			output_batch.add_parallelsentence(parallelsentence)	
		output_batch.close()
	
class BitParserBatchProcessor(BatchProcessor):
	def __init__(self, lang, 
				path,
				lexicon_filename,
				grammar_filename,
				unknownwords,
				openclassdfsa, 
				timeout=30,
				n=100,
				reader=None, 
				writer=None,
				tmpdir="/tmp",
				rootsymbol = "TOP"):
		self.lang = lang
		self.command = []
		if not reader: reader = CEJcmlReader
		if not writer: writer = IncrementalJcml
		self.reader = reader
		self.writer = writer	
		self.tmpdir = tmpdir
		
		self.command = [os.path.join(path,"bitpar"), "-q", "-b", str(n), "-vp", "-s", rootsymbol, "-u", unknownwords, "-w", openclassdfsa, grammar_filename, lexicon_filename] 
		


	def get_features_batch(self, output_textfilename):
		textfile = open(output_textfilename)
		
		output = textfile.read()
		output = re.sub(r"\\([/{}\[\]<>'\$])", r"\1", output).split("\n\n")[:-1]
		#result = []
		for a in output:
			results = a.splitlines()
			if "No parse" in results[0]:
				yield {'bit_failed': 1}
				continue
			probs = [float(a.split("=")[1]) for a in results[::2] if "=" in a]
			trees = [a for a in results[1::2]]
			parses = zip(trees, probs)
			yield get_bitpar_features(parses)
		

	
def get_bitpar_features(parses):
	att = OrderedDict()
	best_parse = sorted(parses)[0]
	att["bit_tree"], att["bit_prob"] = best_parse
	att["bit_n"] = len(parses)
	probabilities = [prob for _, prob in parses]
	att["bit_avgprob"] = average(probabilities)
	att["bit_stdprob"] = std(probabilities)
	att["bit_minprob"] = min(probabilities)
	if att["bit_prob"] > (att["bit_avgprob"] + att["bit_stdprob"]):
		att["bit_probhigh"] = 1
	else:
		att["bit_probhigh"] = 0
	return att


	
if __name__ == '__main__': 
#===============================================================================
# 	parser = BitParChartParser(path="/home/lefterav/tools/bitpar/GermanParser/bin",
# 							lexicon_filename="/home/lefterav/tools/bitpar/GermanParser/Tiger/lexicon",
# 							grammar_filename="/home/lefterav/tools/bitpar/GermanParser/Tiger/grammar",
# 							unknownwords="/home/lefterav/tools/bitpar/GermanParser/Tiger/open-class-tags", 
# 							openclassdfsa="/home/lefterav/tools/bitpar/GermanParser/Tiger/wordclass.txt",
# 							n=100
# 							)
# 	print parser.nbest_parse("der Vorsitzende hat gesagt , dass es eine gute Frage ist .")
# 							
# 							
# 
# 	
#===============================================================================
	path = "/home/lefterav/tools/bitpar/GermanParser/"
	parser = BitParserBatchProcessor(
									lang="de",
									path=os.path.join(path,"bin"),
									lexicon_filename=os.path.join(path,"Tiger/lexicon"),
									grammar_filename=os.path.join(path,"Tiger/grammar"),
									unknownwords=os.path.join(path,"Tiger/open-class-tags"),
									openclassdfsa=os.path.join(path,"Tiger/wordclass.txt"),
									tmpdir=os.path.join(path,"tmp"),
									n=2)
									
	
	input_filename = "/local/research_data/qualitative/dev/learnerLogRegLearnerattattset_24/0.trainingset.jcml"
	output_filename = "/local/research_data/qualitative/dev/learnerLogRegLearnerattattset_24/0.trainingset.bitpar.jcml"
	parser.process_source_batch(input_filename, output_filename)
