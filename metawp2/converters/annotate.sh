#! /bin/bash
SOURCE_LANG=$1
TARGET_LANG=$2
echo "Creating XLIFF parts..."
python ./converters/joshua2xlf.py ../joshua-$SOURCE_LANG-$TARGET_LANG/6-Test.800-decode-trees/default/final/eNBestOut ../joshua-$SOURCE_LANG-$TARGET_LANG/6-Test.800-decode-trees/default/working/inputs/fSentsIn $SOURCE_LANG  $TARGET_LANG ../joshua-$SOURCE_LANG-$TARGET_LANG/6-Test.800-decode-trees/default/working/inputs/weightsFile 1776 1
echo "Creating tar archive..."
tar -czf t1.$SOURCE_LANG-$TARGET_LANG.tar.gz t1-$SOURCE_LANG-$TARGET_LANG
echo "Removing temporary dir..."
rm -rf t1-$SOURCE_LANG-$TARGET_LANG
