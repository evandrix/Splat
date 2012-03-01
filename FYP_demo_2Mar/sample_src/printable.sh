#!/bin/bash

IFS=$'\n'
for NO in $(seq 1 21); do
	OUTPUT=""
	OUTPUT+='<link rel="stylesheet" type="text/css" charset="utf-8" media="all" href="style.css">'
	OUTPUT+="<div class=codearea><pre class=src>"
	line=1
	for i in $(cat "$NO.py"); do
		OUTPUT+="${line}: ${i}$IFS"
		let line=line+1
	done
	OUTPUT+="</div><pre class=bytecode>"
	for i in $(cat "$NO.html"); do
		OUTPUT+="${i}$IFS"
	done
	OUTPUT+="</pre>"
	echo "${OUTPUT}">"${NO}_f.html"
done

for i in $(seq 1 21); do wkpdf -d -m 64 32 32 32 --source "${i}_f.html" --output "${i}_f.pdf"; done
