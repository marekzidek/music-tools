#!/bin/bash
dataset=$1

# IMPORTANT notion:
# the script provided should have all it's arguments "filled in", EXCEPT for the 
# subject of analysis, THE string should end by --part
# The syntactic "space" and the subject to analyze whould be provided by this script
python_script=$2

find $dataset -type f | sort | parallel --progress --joblog "logfile" python3 '$python_script' {}"
