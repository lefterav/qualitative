#!/usr/bin/env bash
set -e

if (( $# != 2 )); then
  echo >&2 "Usage: $0 src-tgt.cooc tgt-src.cooc"
  exit 2
fi

srcTgtCooc=$1
tgtSrcCooc=$2

srcTgtCoocLines=`cat $srcTgtCooc | wc -l`
tgtSrcCoocLines=`cat $tgtSrcCooc | wc -l`

echo "src-tgt.CoocLines $srcTgtCoocLines"
echo "tgt-src.CoocLines $tgtSrcCoocLines"
