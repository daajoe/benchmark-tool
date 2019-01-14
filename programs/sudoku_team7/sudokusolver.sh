FILE=$(readlink -f -- "$0")
DIR=$(dirname "$FILE")

solver="riss"

while [[ "$#" > 0 ]]; do case $1 in
  -g|--glucose) solver="glucose";;
  *) input=$1; break;
esac; shift; done

java -jar "$DIR/SudokuSolver.jar" "$1" "$solver"
