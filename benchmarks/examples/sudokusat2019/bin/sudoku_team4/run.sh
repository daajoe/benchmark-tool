#!/bin/bash

FILE=$(readlink -f -- "$0")
DIR=$(dirname "$FILE")

solver="riss"

while [[ "$#" > 0 ]]; do case $1 in
  -g|--glucose) solver="glucose";;
  *) input=$1;
esac; shift; done

$DIR/ConstraintBuilder/wir-hams-sat "$input" $solver && python3 $DIR/python-checker/main.py temp

RESIDUAL=(output.cnf temp)
rm -r out
for file in ${RESIDUAL[*]}
do
    test -e $file && rm -r $file
done
