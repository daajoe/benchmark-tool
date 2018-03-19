#!/bin/bash
# http://www.cril.univ-artois.fr/~roussel/runsolver/

cd "$(dirname $0)"

#top -n 1 -b > top.txt

[[ -e .finished ]] || python2.7 "{run.root}/programs/genprimal.py" {run.file} | "{run.root}/programs/htd_main" --opt width | sudo "{run.root}/programs/runsolver-3.3.5" \
	-M 8192 \
	-w runsolver.watcher \
	-o runsolver.solver \
	-W {run.timeout} \
	"/home/mzisser/benchmark-tool/programs/{run.solver}" {run.args} -s {run.file}

touch .finished
