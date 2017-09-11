for i in `ls *.submit` 
do
	echo "condor_submit $i"
done
