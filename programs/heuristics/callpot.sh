t=`dirname $1`
cat $1 $2 $t/g.out.$3 | /mnt/vg01/lv01/home/decodyn/src/benchmark-tool/programs/gringo  | /mnt/vg01/lv01/home/decodyn/src/benchmark-tool/programs/clasp-3.3.2 --heuristic=domain --quiet --stats=2 $4                          --opt-strategy=usc,pmres,disjoint,stratify --opt-usc-shrink=min --time-limit=1200 #--configuration=$2

