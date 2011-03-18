# For tool commands, search for '### BEGIN TOOL COMMANDS ###'
function 6-Test2008.800-decode-default {
	set -e     # Stop on errors
	set -o pipefail     # Stop on errors, even if not the last item in a pipe
	#set -v     # Show each original command before it is executed (perhaps WAY before)
	set -x     # Show each command evaluated as it is executed
	# Don't spam the user's bash history and crowd out their favorite incantations
	export HISTFILE=
	cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
	LOON_DIR=`cat /home/elav01/tools/loonybin/paths/loonybin-scripts.path`
	export PATH=.:$LOON_DIR:$PATH
	step=6-Test2008.800-decode
	ambiguity=default
	# Wait for lock file if another competing process is running
	while [[ -e /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock ]]; do
	   echo "Waiting for lock from $(cat /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock)"
	   echo "Waiting for lock from $(cat /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock)" > lockStatus
		trap "rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock.WAIT" EXIT
	   sleep 5
	done
	rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock.WAIT
	
	if [[ ! -e 6-Test2008.800-decode-default.loon ]]; then
		trap "rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock" EXIT
		echo "$(hostname) $$" >/share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock
		# My parents are: 1-BuildLM.530-reuse-default({lm=/share/emplus/shared-tasks/wmt10/lm/news.en.lm.gz}), 0d-test2008.tokenize-default({}), 5-Tune.700-tune-default({spanLimit=10, markOovs=false, includeAlign=false, maxIts=10, heapSizeInMegs=64000, nBest=300, metric=BLEU 4 closest, numThreads=4, treeNBest=false, maxItemsPerBin=40, useDefaultGlue=true, uniqueNBest=true, defaultNonterm=X, nbestSize=300, itemRelativeThreshold=10.0, lmOrder=5, randomRestarts=4, stopSig=0.0001}), 6-Test2008.extract-grammar-default({JVMOptions=-Xmx32G}), 
		# My children are: 
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		mkdir -p /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -rf 6-Test2008.800-decode/default/working   # Remove any partial output
		mkdir -p 6-Test2008.800-decode/default/working
		cd 6-Test2008.800-decode/default/working
		
		if	 [[ ! -e copy.completed ]]; then
			# Prepare necessary inputs for this step using policy: DefaultUnixPolicy
			# Put files into place before running
			rm -f 6-Test2008.800-decode-default.copy.loon # Remove partial logs
			loon-begin-copy 6-Test2008.800-decode-default.copy.loon
			mkdir -p inputs
			ln -sf ../../../../1-BuildLM.530-reuse/default/final/lm inputs/lmFile
			mkdir -p inputs
			ln -sf ../../../../0d-test2008.tokenize/default/final/normalizedCorpus inputs/fSentsIn
			mkdir -p inputs
			ln -sf ../../../../5-Tune.700-tune/default/final/finalParams inputs/weightsFile
			mkdir -p inputs
			ln -sf ../../../../6-Test2008.extract-grammar/default/final/englishGrammar inputs/tmFile
			loon-end-copy 6-Test2008.800-decode-default.copy.loon
			cat 6-Test2008.800-decode-default.copy.loon >> 6-Test2008.800-decode-default.loon
			touch copy.completed
		fi
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode/default/working
		# Check for existance of necessary inputs (symlinks could be broken or policy could be corrupt)
		if test ! -e inputs/tmFile; then echo >&2 "Step does not have required input file: inputs/tmFile"; exit 1; fi
		if test ! -e inputs/lmFile; then echo >&2 "Step does not have required input file: inputs/lmFile"; exit 1; fi
		if test ! -e inputs/fSentsIn; then echo >&2 "Step does not have required input file: inputs/fSentsIn"; exit 1; fi
		if test ! -e inputs/weightsFile; then echo >&2 "Step does not have required input file: inputs/weightsFile"; exit 1; fi
		# Dynamically determine the path to each program on this system using system-specific paths in PATH_DIR
		# Symlink all files from required path so that child scripts don't need to worry about environment variables
		if [[ ! -e /home/elav01/tools/loonybin/paths/joshua.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/joshua.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/joshua.path`/* .
		if [[ ! -e /home/elav01/tools/loonybin/paths/joshua-jar.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/joshua-jar.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/joshua-jar.path`/* .
		if [[ ! -e /home/elav01/tools/loonybin/paths/srilm-lib.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/srilm-lib.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/srilm-lib.path`/* .
		if [[ ! -e /home/elav01/tools/loonybin/paths/mt-analyzers.path ]]; then echo >&2 "Path file not found: /home/elav01/tools/loonybin/paths/mt-analyzers.path (please create it and include path to this tool)"; exit 1; fi
		ln -sf `cat /home/elav01/tools/loonybin/paths/mt-analyzers.path`/* .
		
		if	 [[ ! -e logging.completed ]]; then
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.uniqueNBest 'true'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.useDefaultGlue 'true'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.spanLimit '10'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.lmOrder '5'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.numThreads '4'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.nBest '1'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.includeAlign 'false'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.defaultNonterm 'X'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.itemRelativeThreshold '10.0'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.heapSizeInMegs '64000'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.markOovs 'false'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.maxItemsPerBin '40'
			loon-put 6-Test2008.800-decode-default.logging.loon 6-Test2008.800-decode-default.treeNBest 'false'
			cat 6-Test2008.800-decode-default.logging.loon >> 6-Test2008.800-decode-default.loon
			touch logging.completed
		fi
		# Rerun pre-analyzers every time commands are run
		if	 [[ ! -e commands.completed ]]; then
			rm -f 6-Test2008.800-decode-default.preanalysis.loon # Remove partial logs
			loon-begin-preanalyze 6-Test2008.800-decode-default.preanalysis.loon
			./analyze-srilm.py inputs/lmFile | loon-log 6-Test2008.800-decode-default.preanalysis.loon
			loon-end-preanalyze 6-Test2008.800-decode-default.preanalysis.loon
			cat 6-Test2008.800-decode-default.preanalysis.loon >> 6-Test2008.800-decode-default.exec.loon
		fi
		rm -f outputs/eNBestOut
		if	 [[ ! -e commands.completed ]]; then
			rm -f 6-Test2008.800-decode-default.exec.loon # Remove partial logs
			mkdir -p outputs
			loon-begin-step 6-Test2008.800-decode-default.exec.loon
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
			echo 'top_n=1' >> joshua.config
			echo 'use_remote_lm_server=false' >> joshua.config
			echo 'num_parallel_decoders=4' >> joshua.config
			echo 'parallel_files_prefix=.' >> joshua.config
			echo 'save_disk_hg=false' >> joshua.config
			sed 's/||| //g' inputs/weightsFile >> joshua.config
			export LD_LIBRARY_PATH=.
			java  -classpath joshua.jar -Djava.library.path=./lib -Xmx64000M joshua.decoder.JoshuaDecoder joshua.config inputs/fSentsIn outputs/eNBestOut
			### END TOOL COMMANDS ###
			loon-end-step 6-Test2008.800-decode-default.exec.loon
			cat 6-Test2008.800-decode-default.exec.loon >> 6-Test2008.800-decode-default.loon
			touch commands.completed
		fi
		# Run output finalizers (from policy)
		# Make sure this step fulfilled its contract to produce the required output files
		# And remove write access since no future steps should need to write to these files (and if they did it would introduce ordering effects)
		if test ! -e outputs/eNBestOut ; then echo >&2 "Step did not produce required output file: outputs/eNBestOut"; exit 1; else set +e; chmod -f a-w "outputs/eNBestOut"; set -e; fi
		if	 [[ ! -e postanalysis.completed ]]; then
			rm -f 6-Test2008.800-decode-default.postanalysis.loon # Remove partial logs
			loon-begin-postanalyze 6-Test2008.800-decode-default.postanalysis.loon
			extract_feature_data.py outputs/eNBestOut inputs/weightsFile | loon-log 6-Test2008.800-decode-default.postanalysis.loon
			loon-end-postanalyze 6-Test2008.800-decode-default.postanalysis.loon
			cat 6-Test2008.800-decode-default.postanalysis.loon >> 6-Test2008.800-decode-default.loon
			touch postanalysis.completed
		fi
		# Symlink files into final directory and gzip non-streamable files requesting compression
		(mkdir -p ../final
		cd ../final
		ln -sf ../working/6-Test2008.800-decode-default.loon
		ln -sf ../working/outputs/eNBestOut
		)
		
		# 
		(mkdir -p ../final
		cd ../final
		ln -sf ../working/6-Test2008.800-decode-default.loon
		)
		
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		cp /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode/default/final/6-Test2008.800-decode-default.loon .
		# Concatenate the loonlog files of all parent steps
		loon-cat 6-Test2008.800-decode-default.loon \
			1-BuildLM.530-reuse-default.loon \
			0d-test2008.tokenize-default.loon \
			5-Tune.700-tune-default.loon \
			6-Test2008.extract-grammar-default.loon
		
		mkdir -p 6-Test2008.800-decode/default
		echo 'echo eNBestOut' >> 6-Test2008.800-decode/default/list-files
		echo 'ls /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode/default/working/outputs/eNBestOut' >> 6-Test2008.800-decode/default/list-files
		if [[ -e 6-Test2008.800-decode/default/list-files ]]; then chmod a+x 6-Test2008.800-decode/default/list-files; fi
	fi
	cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
   rm -f /share/accurat/tmp.elav01/wmt11/joshua-de-en-final/6-Test2008.800-decode-default.lock
echo done > .6-Test2008.800-decode-default-pid
} # end function 6-Test2008.800-decode-default

6-Test2008.800-decode-default
function remove-6-Test2008.800-decode-default {
	echo Really remove 6-Test2008.800-decode default? [y/n]
	read YN
	if [[ "$YN" == "y" ]]; then
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -f 6-Test2008.800-decode-default.loon
		cd /share/accurat/tmp.elav01/wmt11/joshua-de-en-final
		rm -rf 6-Test2008.800-decode/default
	fi
	set +e; remove-6-Test2008.810-disambig-default
}
