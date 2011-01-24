#!/usr/bin/env bash
set -e

if (( $# != 4 )); then
  echo >&2 "Usage: $0 src.vcb tgt.vcb src-tgt.snt tgt-src.snt"
  exit 2
fi

srcVcb=$1
tgtVcb=$2
srcTgtSnt=$3
tgtSrcSnt=$4

srcVcbLines=`cat $srcVcb | wc -l`
tgtVcbLines=`cat $tgtVcb | wc -l`
srcTgtSntLines=`cat $srcTgtSnt | wc -l`
tgtSrcSntLines=`cat $tgtSrcSnt | wc -l`

echo "src.VcbLines $srcVcbLines"
echo "tgt.VcbLines $tgtVcbLines"
echo "src-tgt.SntLines $srcTgtSntLines"
echo "tgt-src.SntLines $tgtSrcSntLines"