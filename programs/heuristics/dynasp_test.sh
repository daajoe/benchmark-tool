#bash instance encoding translator_params clasp_params converter_params dflatconverter_params
echo "bash instance encoding dflat/dynasp_params clasp_params converter_params dflatconverter_params"
pid=$$
#clean ordering
#echo "" > g.inp.translator.$pid
echo "USING: $pid"

echo "GRINGOing..."
gringo $1 $2 > g.inp.$pid
echo "GRINGO done"
echo "DYNASPing..."
#TODO: add parameters via command line argument
#-bb: variable ordering instead of -b: tree decomposition
#cat g.inp.$pid | dynasp2 -d  $3             -bb -s $RANDOM -c 2         -s $pid #-bb
cat g.inp.$pid | dynasp -d               -bb $3 -c 6         -s $pid #-bb
echo "DYNASP done"
echo "REVERSE_GRINGOing..."
#sz=$(wc -c < "g.inp.dynasp.$pid")
#if [ $sz -le 4 ]
#then
#	python ReverseGringo.py g.inp.$pid g.inp.translator.$pid $5 > g.out2.$pid
#else
	python ReverseGringo.py g.inp.$pid g.inp.dynasp.$pid $6 > g.out2.$pid
#fi
echo "REVERSE_GRINGO done"
echo "DYN2ASPing..."
cat g.out2.$pid | python Dyn2ASP.py $6 > g.out.$pid
if [ $(wc -c < g.out.$pid) -le 4 ]      #variable ordering mode
then
	cp g.out2.$pid g.out3.$pid
        cp g.out2.$pid g.out.$pid
fi
echo "DYN2ASP done"
#echo "GRINGOing2..."
#gringo $2 $1 g.reverse.$pid > g.out.$pid
#echo "GRINGO2 done"
echo "CLASPing..."
/usr/bin/time ./callpot.sh $1 $2 $pid $4 > out.$pid
#\time clasp --quiet --opt-strategy=bb --stats=2 --heuristic=domain --configuration=$3 $4 < gringoout2
echo "CLASP done"
cat out.$pid
