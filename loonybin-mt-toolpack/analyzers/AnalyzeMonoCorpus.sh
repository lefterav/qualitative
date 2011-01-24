#!/usr/bin/env bash
set -e

if [ $# != 1 ]; then
  echo >&2 "Usage: $0 monoCorpusFile"
  exit 2
fi

corpus=$1
dir=`dirname $0`

# TODO: Support dev corpus for mono corpus
numFolds=10
stats="`$dir/CalcParCorpusStats.py $numFolds $corpus`"
