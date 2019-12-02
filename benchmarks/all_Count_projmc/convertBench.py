import sys
import os.path
import random

f = file(sys.argv[1], "r")
fproj = file(sys.argv[2], "r")
pth = "converted"
try:
	os.makedirs(pth)
except:
	pass
f2 = file("{0}/{1}_{2}.cnf".format(pth,os.path.basename(f.name), os.path.basename(fproj.name)), "w")
for r in f:
	f2.write(r)
	if r.startswith("p "):
		proj=fproj.readline().replace("\n","")
		fproj.close()
		spl = proj.split(",")
		f2.write("c ind {0} 0\n".format(" ".join(map(str,spl))))
f2.close()
f.close()
