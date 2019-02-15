import sys

f = file(sys.argv[1], "r")
c = 0
at = {}
for line in iter(f):
	if c > 0 and not line.startswith("c") and not line.startswith("p") and not line.startswith("%"):
		p = line.split(" ")
		try:
			nonempty = False
			for i in p:
				if i != "":
	 				i = int(i)
					if i != 0:
						nonempty = True
						if i > 0:
							print "pos(c{},a{}). ".format(c, i)
							at[i] = True
						else:
							print "neg(c{},a{}). ".format(c, -i)
							at[-i] = True
			if nonempty:
				print "clause(c{}). ".format(c)
		except ValueError:
			pass
	c += 1

f.close()

for i in at:
	print "atom(a{}). ".format(i)
	
