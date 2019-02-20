#!/bin/bash

THISFILE=$(readlink -f -- "${0}")
THISDIR=${THISFILE%/*}

solver="riss"

while [[ "$#" > 0 ]]; do case $1 in
  -g|--glucose) solver="glucose -model";;
  *) input=$1;
esac; shift; done

size=$(python $THISDIR/parse_input.py "$input")

# echo "Start SAT Solving"
$THISDIR/streamer $size | $solver > out.txt
# cat out.txt | grep CPU
# cat out.txt | grep SAT
python $THISDIR/parse_output.py $size
cat result.txt
# echo "The output is: "
# ./sudotest-linux64 -f result.txt
