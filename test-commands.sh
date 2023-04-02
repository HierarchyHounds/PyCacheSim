#!/bin/bash

OUTPUT_DIRECTORY=output

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

function run_test_case {
	# read the filename as the first command line argument
	line="$@"
	printf "Test case $i.\n$line\n"
	python sim_cache.py $line >$OUTPUT_DIRECTORY/$i.txt || exit $?
	printf "Output saved to: $OUTPUT_DIRECTORY/$i.txt\n"

	# if validation file exists, compare output
	test -f assets/output/validation$i.txt && diff_output assets/output/validation$i.txt $OUTPUT_DIRECTORY/$i.txt
	i=$((i + 1))
}

function diff_output {
	printf "Comparing output against validation file... "
	diff_file=$OUTPUT_DIRECTORY/diff$i.txt
	diff -iwy --suppress-common-lines $1 $2 >$diff_file
	if [ $? -eq 0 ]; then
		printf "Match."
	elif [ $? -eq 1 ]; then
		printf "Mismatch. See $diff_file"
	else
		printf "Error."
		exit $?
	fi
	printf "\n\n"
	return 0
}

while read line; do
	run_test_case $line

done <$filename
