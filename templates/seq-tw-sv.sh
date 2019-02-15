#!/bin/bash
# http://www.cril.univ-artois.fr/~roussel/runsolver/

#CAT="{run.root}/programs/gcat.sh"
source ~/.bashrc

cd "$(dirname $0)"

#top -n 1 -b > top.txt

printf 'hostname is ' >> runsolver.err
hostname >> runsolver.err

temp=$(mktemp -d -p /dev/shm -t tmp.SAT-TW.XXXXXXXXX)
#echo "Created temp working directory $temp"

#template does not support curly brackets
function cleanup() if [[ $temp == /dev/shm/tmp.* ]] ; then rm -r $temp; fi; echo "Deleted temp working directory $temp"

trap cleanup EXIT


core=$(($1+2))

#[[ -e .finished ]] || $CAT "{run.file}" | "{run.root}/programs/runsolver-3.3.4" \
[[ -e .finished ]] ||  taskset -c $core "{run.root}/programs/runsolver-3.3.1" \
	-M 20000 \
	-w runsolver.watcher \
	-W {run.timeout} \
	"{run.root}/programs/{run.solver}" {run.args} -p $temp -f "{run.file}" > runsolver.solver 2>>runsolver.err

touch .finished
