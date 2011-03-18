# For tool commands, search for '### BEGIN TOOL COMMANDS ###'
function 5-Tune.700-tune-default {
	set -e     # Stop on errors
	set -o pipefail     # Stop on errors, even if not the last item in a pipe
	#set -v     # Show each original command before it is executed (perhaps WAY before)
	set -x     # Show each command evaluated as it is executed
	# Don't spam the user's bash history and crowd out their favorite incantations
	export HISTFILE=
	cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
	LOON_DIR=`cat /home/elav01/tools/loonybin/paths/loonybin-scripts.path`
	export PATH=.:$LOON_DIR:$PATH
	step=5-Tune.700-tune
	ambiguity=default
	# Wait for lock file if another competing process is running
	while [[ -e /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock ]]; do
	   echo "Waiting for lock from $(cat /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock)"
	   echo "Waiting for lock from $(cat /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock)" > lockStatus
		trap "rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock.WAIT" EXIT
	   sleep 5
	done
	rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock.WAIT
	
	if [[ ! -e 5-Tune.700-tune-default.loon ]]; then
		trap "rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock" EXIT
		echo "$(hostname) $$" >/share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock
		# My parents are: 5-Tune.700-extract-grammar-default({JVMOptions=-Xmx60G}), 5-Tune.weightsFile-default({paramConfigFile=/home/elav01/experiments/metawp2/joshua-run/init/params.txt}), 0a-dev.lowercase-e-default({}), 0a-dev.lowercase-f-default({}), 1-BuildLM.530-reuse-default({lm=/share/emplus/shared-tasks/wmt10/lm/news.en.lm.gz}), 
		# My children are: 
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		mkdir -p /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -rf 5-Tune.700-tune/default/working   # Remove any partial output
		mkdir -p 5-Tune.700-tune/default/working
		cd 5-Tune.700-tune/default/working
		
		if	 [[ ! -e copy.completed ]]; then
			# Prepare necessary inputs for this step using policy: DefaultUnixPolicy
			# Put files into place before running
			rm -f 5-Tune.700-tune-default.copy.loon # Remove partial logs
			loon-begin-copy 5-Tune.700-tune-default.copy.loon
			mkdir -p inputs
			ln -sf ../../../../5-Tune.700-extract-grammar/default/final/englishGrammar inputs/tmFile
			mkdir -p inputs
			ln -sf ../../../../5-Tune.weightsFile/default/final/paramConfigFile inputs/paramConfigFile
			mkdir -p inputs
			ln -sf ../../../../0a-dev.lowercase-e/default/final/normalizedCorpus inputs/eRefSents
			mkdir -p inputs
			ln -sf ../../../../0a-dev.lowercase-f/default/final/normalizedCorpus inputs/fDevSents
			mkdir -p inputs
			ln -sf ../../../../1-BuildLM.530-reuse/default/final/lm inputs/lmFile
			loon-end-copy 5-Tune.700-tune-default.copy.loon
			cat 5-Tune.700-tune-default.copy.loon >> 5-Tune.700-tune-default.loon
			touch copy.completed
		fi
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune/default/working
		# Check for existance of necessary inputs (symlinks could be broken or policy could be corrupt)
		if test ! -e inputs/fDevSents; then echo >&2 "Step does not have required input file: inputs/fDevSents"; exit 1; fi
		if test ! -e inputs/eRefSents; then echo >&2 "Step does not have required input file: inputs/eRefSents"; exit 1; fi
		if test ! -e inputs/tmFile; then echo >&2 "Step does not have required input file: inputs/tmFile"; exit 1; fi
		if test ! -e inputs/paramConfigFile; then echo >&2 "Step does not have required input file: inputs/paramConfigFile"; exit 1; fi
		if test ! -e inputs/lmFile; then echo >&2 "Step does not have required input file: inputs/lmFile"; exit 1; fi
		# Dynamically determine the path to each program on this system using system-specific paths in PATH_DIR
		# Symlink all files from required path so that child scripts don't need to worry about environment variables
		if [[ ! -e /home/elav01/tools/loonybin/paths/joshua.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/joshua.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/joshua.path`/* .
		if [[ ! -e /home/elav01/tools/loonybin/paths/srilm-lib.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/srilm-lib.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/srilm-lib.path`/* .
		if [[ ! -e /home/elav01/tools/loonybin/paths/mt-analyzers.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/mt-analyzers.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/mt-analyzers.path`/* .
		
		if	 [[ ! -e logging.completed ]]; then
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.uniqueNBest 'true'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.useDefaultGlue 'true'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.spanLimit '10'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.lmOrder '5'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.numThreads '4'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.nBest '300'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.includeAlign 'false'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.defaultNonterm 'X'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.itemRelativeThreshold '10.0'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.maxIts '10'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.stopSig '0.0001'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.metric 'BLEU 4 closest'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.randomRestarts '4'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.heapSizeInMegs '64000'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.nbestSize '300'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.markOovs 'false'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.maxItemsPerBin '40'
			loon-put 5-Tune.700-tune-default.logging.loon 5-Tune.700-tune-default.treeNBest 'false'
			cat 5-Tune.700-tune-default.logging.loon >> 5-Tune.700-tune-default.loon
			touch logging.completed
		fi
		# Rerun pre-analyzers every time commands are run
		if	 [[ ! -e commands.completed ]]; then
			rm -f 5-Tune.700-tune-default.preanalysis.loon # Remove partial logs
			loon-begin-preanalyze 5-Tune.700-tune-default.preanalysis.loon
			./analyze-srilm.py inputs/lmFile | loon-log 5-Tune.700-tune-default.preanalysis.loon
			java -cp ParCorpusAnalyzer.jar analyzers.PhraseTableAnalyzer inputs/tmFile | loon-log 5-Tune.700-tune-default.preanalysis.loon
			loon-end-preanalyze 5-Tune.700-tune-default.preanalysis.loon
			cat 5-Tune.700-tune-default.preanalysis.loon >> 5-Tune.700-tune-default.exec.loon
		fi
		rm -f outputs/finalParams
		rm -f outputs/eNBestOut
		if	 [[ ! -e commands.completed ]]; then
			rm -f 5-Tune.700-tune-default.exec.loon # Remove partial logs
			mkdir -p outputs
			loon-begin-step 5-Tune.700-tune-default.exec.loon
			### BEGIN TOOL COMMANDS ###
			echo "[S] ||| [X,1] ||| [X,1] ||| 0 0 0" >> hiero.glue
			echo "[S] ||| [S,1] [X,2] ||| [S,1] [X,2] ||| 0.434294482 0 0" >> hiero.glue
			echo 'lm_file=inputs/lmFile' >> joshua.config
			echo 'tm_format=hiero' >> joshua.config
			echo 'tm_file=inputs/tmFile' >> joshua.config
			echo 'goal_symbol=S' >> joshua.config
			echo 'glue_format=hiero' >> joshua.config
			echo 'glue_file=hiero.glue' >> joshua.config
			echo 'use_srilm=true' >> joshua.config
			echo 'lm_ceiling_cost=100' >> joshua.config
			echo 'use_left_equivalent_state=false' >> joshua.config
			echo 'use_right_equivalent_state=false' >> joshua.config
			echo 'order=5' >> joshua.config
			echo '#TM config' >> joshua.config
			echo 'span_limit=10' >> joshua.config
			echo 'phrase_owner=pt' >> joshua.config
			echo 'mono_owner=mono' >> joshua.config
			echo 'begin_mono_owner=begin_mono' >> joshua.config
			echo 'default_non_terminal=X' >> joshua.config
			echo 'goalSymbol=S' >> joshua.config
			echo 'mark_oovs=false' >> joshua.config
			echo 'fuzz1=0.1' >> joshua.config
			echo 'fuzz2=0.1' >> joshua.config
			echo 'max_n_items=40' >> joshua.config
			echo 'relative_threshold=10.0' >> joshua.config
			echo 'max_n_rules=50' >> joshua.config
			echo 'rule_relative_threshold=10.0' >> joshua.config
			echo 'use_unique_nbest=true' >> joshua.config
			echo 'use_tree_nbest=false' >> joshua.config
			echo 'include_align_index=false' >> joshua.config
			echo 'add_combined_cost=true' >> joshua.config
			echo 'top_n=300' >> joshua.config
			echo 'use_remote_lm_server=false' >> joshua.config
			echo 'num_parallel_decoders=4' >> joshua.config
			echo 'parallel_files_prefix=.' >> joshua.config
			echo 'save_disk_hg=false' >> joshua.config
			numRefs=$(( $( wc -l < inputs/eRefSents ) / $( wc -l < inputs/fDevSents ) ))
			echo "-maxIt 10" >> zmert.config
			echo "-r inputs/eRefSents" >> zmert.config
			echo "-ipi 4" >> zmert.config
			echo "-rand 0" >> zmert.config
			echo "-v 1" >> zmert.config
			echo "-stopSig 0.0001" >> zmert.config
			echo "-seed 12341234" >> zmert.config
			echo "-m BLEU 4 closest" >> zmert.config
			echo "-dir ." >> zmert.config
			echo "-dcfg joshua.config" >> zmert.config
			echo "-N 300" >> zmert.config
			echo "-decV 1" >> zmert.config
			echo "-p params.txt" >> zmert.config
			echo "-decOut nbest.out" >> zmert.config
			echo "-rps $numRefs" >> zmert.config
			echo "-s inputs/fDevSents" >> zmert.config
			echo "-fin outputs/finalParams" >> zmert.config
			sed 's/|||.*/ 0.0/g;s/normalization.*//g' inputs/paramConfigFile >> joshua.config
			cp inputs/paramConfigFile params.txt
			echo "java -Xmx1g -cp ./bin/joshua.jar -Djava.library.path=./lib -Dfile.encoding=utf8 joshua.decoder.JoshuaDecoder joshua.config inputs/fDevSents devset.output.nbest" > decoder_command
			export LD_LIBRARY_PATH=.
			java -cp bin/joshua.jar -Xmx64000M -Djava.library.path=./lib joshua.zmert.ZMERT zmert.config | tee zmert.stdout
			dir=`pwd`
			file=`ls -1t nbest.out.ZMERT.it* | head -1`
			ln -s $dir/$file outputs/eNBestOut
			### END TOOL COMMANDS ###
			loon-end-step 5-Tune.700-tune-default.exec.loon
			cat 5-Tune.700-tune-default.exec.loon >> 5-Tune.700-tune-default.loon
			touch commands.completed
		fi
		# Run output finalizers (from policy)
		# Make sure this step fulfilled its contract to produce the required output files
		# And remove write access since no future steps should need to write to these files (and if they did it would introduce ordering effects)
		if test ! -e outputs/finalParams ; then echo >&2 "Step did not produce required output file: outputs/finalParams"; exit 1; else set +e; chmod -f a-w "outputs/finalParams"; set -e; fi
		if test ! -e outputs/eNBestOut ; then echo >&2 "Step did not produce required output file: outputs/eNBestOut"; exit 1; else set +e; chmod -f a-w "outputs/eNBestOut"; set -e; fi
		if	 [[ ! -e postanalysis.completed ]]; then
			rm -f 5-Tune.700-tune-default.postanalysis.loon # Remove partial logs
			touch postanalysis.completed
		fi
		# Symlink files into final directory and gzip non-streamable files requesting compression
		(mkdir -p ../final
		cd ../final
		ln -sf ../working/5-Tune.700-tune-default.loon
		ln -sf ../working/outputs/finalParams
		ln -sf ../working/outputs/eNBestOut
		)
		
		# 
		(mkdir -p ../final
		cd ../final
		ln -sf ../working/5-Tune.700-tune-default.loon
		)
		
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		cp /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune/default/final/5-Tune.700-tune-default.loon .
		# Concatenate the loonlog files of all parent steps
		loon-cat 5-Tune.700-tune-default.loon \
			5-Tune.700-extract-grammar-default.loon \
			5-Tune.weightsFile-default.loon \
			0a-dev.lowercase-e-default.loon \
			0a-dev.lowercase-f-default.loon \
			1-BuildLM.530-reuse-default.loon
		
		mkdir -p 5-Tune.700-tune/default
		echo 'echo finalParams' >> 5-Tune.700-tune/default/list-files
		echo 'ls /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune/default/working/outputs/finalParams' >> 5-Tune.700-tune/default/list-files
		echo 'echo eNBestOut' >> 5-Tune.700-tune/default/list-files
		echo 'ls /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune/default/working/outputs/eNBestOut' >> 5-Tune.700-tune/default/list-files
		if [[ -e 5-Tune.700-tune/default/list-files ]]; then chmod a+x 5-Tune.700-tune/default/list-files; fi
	fi
	cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
   rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/5-Tune.700-tune-default.lock
echo done > .5-Tune.700-tune-default-pid
} # end function 5-Tune.700-tune-default

5-Tune.700-tune-default
function remove-5-Tune.700-tune-default {
	echo Really remove 5-Tune.700-tune default? [y/n]
	read YN
	if [[ "$YN" == "y" ]]; then
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -f 5-Tune.700-tune-default.loon
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -rf 5-Tune.700-tune/default
	fi
	set +e; remove-6-Test2008.800-decode-default
	set +e; remove-6-Test2010.800-decode-default
	set +e; remove-6-Test2011.800-decode-default
	set +e; remove-6-Test2011.800-decode-default
	set +e; remove-6-Test2010.800-decode-default
	set +e; remove-6-Test2008.800-decode-default
	set +e; remove-6-Test2008.800-decode-default
	set +e; remove-6-Test2008.800-decode-default
	set +e; remove-6-Test2008.800-decode-default
}
