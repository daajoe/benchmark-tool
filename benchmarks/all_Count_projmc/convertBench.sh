for i in `ls`
do
	echo $i	
	for j in `ls $i/*.cnf`
	do
		echo $j
		for k in `ls $i/*.var`
		do
			echo $k	
			python `dirname ${BASH_SOURCE[0]}`/convertBench.py $j $k
		done
	done
done
