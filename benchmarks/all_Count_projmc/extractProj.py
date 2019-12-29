#!/usr/bin/python
import sys
import os.path
import random

f = file(sys.argv[1], "r")
proj = []
for r in f:
	if r.startswith("c ind"):
		var = r.split(" ")[2:-1]
		proj += var
f.close()
#print proj
print(",".join(proj))
