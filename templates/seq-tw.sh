#!/bin/bash
# http://www.cril.univ-artois.fr/~roussel/runsolver/

#CAT="{run.root}/programs/gcat.sh"

cd "$(dirname $0)"

#top -n 1 -b > top.txt

#[[ -e .finished ]] || $CAT "{run.file}" | "{run.root}/programs/runsolver-3.3.4" \
[[ -e .finished ]] ||  "{run.root}/programs/runsolver-3.3.1" \
	-M 20000 \
	-w runsolver.watcher \
	#-o runsolver.solver \
	#-W {run.timeout} \
	"{run.root}/programs/{run.solver}" {run.args} -f "{run.file}" > runsolver.solver 2>runsolver.err

touch .finished
