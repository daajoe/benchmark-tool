THISFILE=$(readlink -f -- "${0}")
THISDIR=${THISFILE%/*}

SIZE=$(python $THISDIR/parse_input.py "$1")
# echo "Start SAT Solving"
$THISDIR/streamer $SIZE | riss > out.txt
# cat out.txt | grep CPU
# cat out.txt | grep SAT
python $THISDIR/parse_output.py $SIZE
cat result.txt
# echo "The output is: "
# ./sudotest-linux64 -f result.txt
