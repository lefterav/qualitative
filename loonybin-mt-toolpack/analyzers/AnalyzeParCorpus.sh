#!/usr/bin/env bash
set -e

if [ $# != 2 ]; then
  echo >&2 "Usage: $0 parallel_corpus.src parallel_corpus.tgt [dev_corpus.src dev_corpus.tgt]"
  exit 2
fi

srcCorpus=$1
tgtCorpus=$2
dir=`dirname $0`

numFolds=5
java -jar $dir/ParCorpusAnalyzer.jar $numFolds $@

