#!/usr/bin/env bash

if [[ ! -x `which loon` ]]; then
    echo loon command not found on your PATH
    exit 1
fi

testDir=test
mkdir -p $testDir
for workflow in `ls workflows`; do
    echo Testing workflows/$workflow
    java -cp $(dirname $(which loon))/bin:`find $(dirname $(which loon))/lib $(dirname $(which loon))/ivy -name '*.jar' | awk '{printf $1":"}'` loony.ui.LoonyBinConsole -g workflows/$workflow $testDir/$workflow.sh all
    #loon -g workflows/$workflow $testDir/$workflow.sh all
    if [[ $? == 0 ]]; then
	echo "PASSED: $workflow"
    else
	echo "FAILED: $workflow"
    fi
    echo
done

# 1) SRILM

# 2) LM Filter

# 3) AER Tool

# 4) Stanford Parser?

# 5) Berkeley Aligner

# 6) Joshua

# 7) Moses

# 8) SAMT

# 9) MGIZA / ForceAlign

# 10) Chaski

# 11) MEMT
