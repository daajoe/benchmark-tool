import sys

assert(len(sys.argv) >= 4)
fgringo = file(sys.argv[1], "r")
ftreede = file(sys.argv[2], "r")
funcAllowed = sys.argv[3].split(",")

REORGANIZE_NBR_SPACE = True
CLEAN_UP_HEUR = True
START_REORG = 1

inmap = False
gringomap = {}
roots = {}
bag = {}

for l in fgringo:
	#print l
	if l.startswith("0"):
		inmap = not inmap
		if not inmap:
			break
	elif inmap:
		ll = l.split(" ")
		assert(len(ll) == 2)
		gringomap[ll[0]] = ll[1].strip()

fgringo.close()

def startsIn(s, ls):
	for l in ls:
		if s.startswith(l):
			return True
	return False

for l in ftreede:
	if l.startswith("_heuristic"):
		ls = l.split("(")
		assert(len(ls) == 2)
		lss = ls[1].split(")")
		assert(len(lss) == 2)
		inner = lss[0].split(",")
		assert(len(inner) <= 2)

		#result = ls[0] + "(" 
		k = gringomap.get(inner[0])
		if not k is None:
			#TODO: make general
			if not CLEAN_UP_HEUR or startsIn(k, funcAllowed): #k.startswith("in"):
				roots[k] = inner[1]
				lst = bag.get(inner[1])
				if lst is None:
					lst = []
					bag[inner[1]] = lst
				lst.append(k)
				#result += "" + k + ",init," + inner[1]
		#else:
		#	result = None
		#if not result is None:	
		#	result += ")" + lss[1]
		#	print result,
		
	elif l.find("(") < 0 or (not l.startswith("intro") and not l.startswith("current(") and not l.startswith("forgotten") and not l.startswith("-intro")):
		print l,
	elif l.startswith("intro") or l.startswith("current") or l.startswith("child"):
		ls = l.split("(")
		assert(len(ls) == 2)
		lss = ls[1].split(")")
		assert(len(lss) == 2)
		inner = lss[0].split(",")
		assert(len(inner) <= 2)

		result = ls[0] + "(" 
		k = ""
		for i in inner:
			if k != "":
				result += ","
			#print i
			#print gringomap
			#assert(False)
			k = gringomap.get(i)
			if not k is None:
				result += k
			else:
				result = None
				break
				#result += i
		if not result is None:	
			result += ")" + lss[1]
			print result,
		
if REORGANIZE_NBR_SPACE:
	keys = bag.keys() 
	keys.sort()
	i = START_REORG
	for v in keys:
		for k in bag[v]:
			roots[k] = i
			i += 1
for k in roots:
	#print k
	print "_heuristic({},init,{}).".format(k, roots[k])

