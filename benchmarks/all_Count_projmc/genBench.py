import sys
import os.path
import random

random.seed(int(sys.argv[2]))

for p in range(2,15,2):
	for tr in range(1,3,1):
		f = file(sys.argv[1], "r")
		pth = "proj{0}".format(p)
		try:
			os.makedirs(pth)
		except:
			pass
		f2 = file("{0}/{1}{2}_{3}.cnf".format(pth,os.path.basename(f.name), p, tr), "w")
		for r in f:
			f2.write(r)
			if r.startswith("p "):
				ls = r.split(" ")
				spl = random.sample(list(range(1,int(ls[2]) + 1,1)), p)
				f2.write("a {0} 0\n".format(" ".join(map(str,spl))))
		f2.close()
		f.close()

