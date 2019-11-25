for i in `ls ../all_Count_pmc`
do
	echo $i	
	python genBench.py ../all_Count_pmc/$i 14134
done
