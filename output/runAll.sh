#!/bin/bash

JOB_START=10000
OUT_FILE="doneCmds4.sh"

function checkJobs {	
	echo `condor_q hecher | grep '[0-9]* jobs' | sed 's/[^0-9].*//'`
}

#clean output file
echo > $OUT_FILE

while IFS='' read -r line || [[ -n "$line" ]]; do

	val=$(checkJobs)
	echo $val

	while [[ $val -gt $JOB_START ]] 
	do
		sleep 300

		val=$(checkJobs)
		echo $val
	done

	if [[ $val -lt $JOB_START ]]
	then
		eval $line
		echo $line >> $OUT_FILE
	fi
done

