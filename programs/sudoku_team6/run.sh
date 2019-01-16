#!/bin/bash

FILE=$(readlink -f -- "$0")
DIR=$(dirname "$FILE")

solver="riss"

while [[ "$#" > 0 ]]; do case $1 in
  -g|--glucose) solver="glucose";;
  *) input=$1;
esac; shift; done

$DIR/sudoku-sat "$input" $solver 1> /dev/null
cat output.txt


# Clean up
# RESIDUAL=(CNF.cnf output.txt)
# for file in ${RESIDUAL[*]}
# do
#     test -e $file && rm $file
# done
