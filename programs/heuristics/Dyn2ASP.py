import Dflat2ASP
import sys

if __name__ == "__main__":
	d = Dflat2ASP.Dflat2ASP()
	fi = sys.stdin
	d.parse(fi, sys.stdout)
	de = d.predReader().getRoot()
	allowed = []
	if len(sys.argv) > 1:
		allowed = sys.argv[1].split(",")
	print d.makeProgram(de, "", allowed, True)

