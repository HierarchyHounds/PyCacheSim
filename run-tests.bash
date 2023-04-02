#!/bin/bash

OUTPUT_DIRECTORY=output
VALIDATION_DIRECTORY=assets/output
DEBUG_DIRECTORY=assets/debug
# place validation files at assets/output/validation#.txt
# place debug files at assets/debug/debug#.txt

test -d $OUTPUT_DIRECTORY || {
	printf "Creating output directory: $OUTPUT_DIRECTORY\n"
	mkdir -p $OUTPUT_DIRECTORY
}

# read the filename as the first command line argument
filename=$1

# check if filename is empty
test -z $filename && {
	printf "Usage: $0 <test-cases.txt> [--debug]\n"
	exit 1
}

# check if the file exists
test -f $filename || {
	printf "$filename: not found.\n"
	exit 1
}

DEBUG=false
# check if the second argument is --debug

test "x$2" = "x--debug" && {
	DEBUG=true
	printf "Debug mode enabled.\n"
}

printf "Loading test cases: $filename.\n"

i=0

function run_test_case {
	# read the filename as the first command line argument
	line="$@"
	printf "Test case $i.\n"
	printf "Parameters: $line\n"
	output_file=$OUTPUT_DIRECTORY/output$i.txt
	debug_output_file=$OUTPUT_DIRECTORY/debug$i.txt
	python sim_cache.py $line >$OUTPUT_DIRECTORY/output$i.txt || exit $?
	printf "Output:\t$OUTPUT_DIRECTORY/output$i.txt\n"

	# if validation file exists, compare output
	validation_file=assets/output/validation$i.txt
	test -f $validation_file && {
		printf "Comparing against $validation_file... "
		diff_file=$OUTPUT_DIRECTORY/diff-$i.txt
		diff -wy $output_file $validation_file >$diff_file && printf_green "Match.\n" && rm $diff_file || printf_red "Mismatch. See $diff_file\n"
	}

	# if debug is enabled, run the test case with debug output
	test $DEBUG = true && {
		python sim_cache.py $line --debug >$OUTPUT_DIRECTORY/debug$i.txt || exit $?
		printf "Debug:\t$OUTPUT_DIRECTORY/debug$i.txt\n"
		# if debug validation file exists, compare debug output
		debug_validation_file=assets/debug/debug$i.txt
		test -f assets/debug/debug$i.txt && {
			printf "Comparing against $debug_validation_file... "
			diff_file=$OUTPUT_DIRECTORY/debug-diff-$i.txt
			diff -wy --speed-large-files $debug_output_file $debug_validation_file >$diff_file && printf_green "Match.\n" && rm $diff_file || printf_red "Mismatch. See $diff_file\n"
		}
	}

	i=$((i + 1))
	printf "\n"
}

function printf_green {
	printf "\033[1;32m$@\033[0m"
}

function printf_red {
	printf "\033[1;31m$@\033[0m"
}

while read line; do
	run_test_case $line
done <$filename
