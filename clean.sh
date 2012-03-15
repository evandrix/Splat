#!/bin/bash

rm -rf test_*.{py,json} coverdir
excluded=( 'program' 'fizzbuzz' 'factorial' 'simple' 'hanoi' )
for file in $(ls *.pyc)
do
	to_keep=false
	for i in "${excluded[@]}"
	do
	    if [ "$i.pyc" == "$file" ]; then
	        to_keep=true
	    fi
	done
	if [[ "$file" =~ m[0-9]+\.pyc ]]; then
		to_keep=true
	fi
	if ! $to_keep; then
		rm -f "$file"
	fi
done
