#!/bin/bash

mkdir -p out

i=0
while read line; do
	echo -e "Test $i: $line \t => out/$i.txt"
	python sim_cache.py $line >out/$i.txt
	diff -iw assets/output/validation$i.txt out/$i.txt >out/diff$i.txt
	((i++))
done <test-cases.txt
