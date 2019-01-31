#!/bin/bash
ipt_folder=$1
opt_prefix=$2

list=$(find $ipt_folder -type d | sort -r | awk 'a!~"^"$0{a=$0;print}' | sort)

echo "$list"

while read line; do
	python3 correct_note_offs.py -i "$line" -o "$opt_prefix"/"$(echo $line | cut -d '/' -f2-)"
	python3 separate_channels.py -i "$line" -o "$opt_prefix"/"$(echo $line | cut -d '/' -f2-)"

done <<< "$list"
