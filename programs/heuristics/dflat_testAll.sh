#bash instance encoding translator_params clasp_params converter_params dflatconverter_params
echo "bash instance encoding dflat/dynasp_params clasp_params converter_params dflatconverter_params output EDGE"
pid=$$
#clean ordering
#echo "" > g.inp.translator.$pid
echo "USING: $pid"

echo "DFLATing..."
#Using MCS!
#--elimination min-degree: use variable orderings instead of TDs (still MCS)
dflat2 -s dummy -e $8 --graphml-out g.inp.$pid -f $1 --print-decomposition $3 --heurpred=$5                       --no-empty-root --no-empty-leaves #--elimination min-degree #--path-decomposition
dflat2 -s dummy -e $8 --graphml-out g.xml.$7.$pid -f $1 --print-decomposition $3 --heurpred=$5                        --no-empty-root --no-empty-leaves #--elimination min-degree #--path-decomposition
echo "DFLAT done"
echo "DFLAT2ASPing..."
python Dflat2ASP.py $5 < g.inp.$pid > g.out.$pid
if [ $(wc -c < g.out.$pid) -le 4 ]	#variable ordering mode
then
	cp g.inp.$pid g.out.$pid
fi
echo "DFLAT2ASP done..."
echo "CLASPing..."
gringo $1 $2 g.out.$pid > g.gr.out.$7.$pid.gr
/usr/bin/time ./callpot.sh $1 $2 $pid $4 > g.g.out.$7.$pid.out 2> g.g.out.$7.$pid
echo "CLASP done"
cat g.g.out.$7.$pid >&2
cat g.g.out.$7.$pid.out

