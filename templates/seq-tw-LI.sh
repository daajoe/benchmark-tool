#!/bin/bash
# http://www.cril.univ-artois.fr/~roussel/runsolver/

#CAT="{run.root}/programs/gcat.sh"
source ~/.bashrc

cd "$(dirname $0)"

#top -n 1 -b > top.txt

printf 'hostname is ' >> runsolver.err
hostname >> runsolver.err

[[ -e .finished ]] ||  "{run.root}/programs/runsolver-3.3.5" \
	-M 8196 \
	-w runsolver.watcher \
	-W {run.timeout} \
	"{run.root}/programs/{run.solver}" {run.args} -p $temp -f "{run.file}" > runsolver.solver 2>>runsolver.err

touch .finished
