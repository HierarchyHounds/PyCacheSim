#!/bin/bash

set -e

OUTPUT_DIRECTORY=out

printf "Creating output directory: $OUTPUT_DIRECTORY\n"
mkdir -p $OUTPUT_DIRECTORY

# read the filename as the first command line argument
filename=$1

# check if filename is empty
test -z $filename && {
	printf "Usage: $0 <test-cases.txt>\n"
	exit 1
}

# check if the file exists
test -f $filename || {
	printf "$filename: not found.\n"
	exit 1
}

printf "Loading test cases: $filename.\n"

i=0

printf "Running test cases...\n\n"

function run_test_cases {
	# read the filename as the first command line argument
	line="$@"
	printf "Test case $i.\n$line\n"
	python sim_cache.py $line >out/$i.txt
	printf "Output saved to: out/$i.txt\n"
	test -f assets/output/validation$i.txt &&
		printf "Comparing output against validation file... " &&
		{ diff -iw assets/output/validation$i.txt out/$i.txt >out/diff$i.txt; } && printf "Match." || printf "Mismatch. See out/diff$i.txt for details."
	((i++))
}

while read line; do
	run_test_cases $line || true
	printf "\n\n"
done <$filename
