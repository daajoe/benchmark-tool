#!/usr/bin/python
import sys
import os.path
import random

f = file(sys.argv[1], "r")
for r in f:
	if r.startswith("c ind"):
		var = r.split(" ")[2:-1]
		print(",".join(var))
		break
f.close()
