#!/bin/bash

FILE=$(readlink -f -- "$0")
DIR=$(dirname "$FILE")
$DIR/sudoku-sat $@ 1> /dev/null && cat output.txt


# Clean up
# RESIDUAL=(CNF.cnf output.txt)
# for file in ${RESIDUAL[*]}
# do
#     test -e $file && rm $file
# done
